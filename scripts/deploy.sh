#!/bin/bash
# 邮件助手 - 百度云服务器部署脚本
# 在服务器上执行此脚本完成部署

set -e  # 遇到错误立即退出

echo "========================================"
echo "📧 邮件助手 - 服务器部署脚本"
echo "========================================"

# 配置
INSTALL_DIR="/opt/email-assistant"
LOG_DIR="/var/log/email-assistant"
SERVICE_USER="emailbot"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 用户运行此脚本"
    echo "   运行: sudo bash deploy.sh"
    exit 1
fi

echo ""
echo "📝 步骤 1/7: 安装系统依赖..."
apt-get update > /dev/null 2>&1
apt-get install -y python3 python3-pip python3-venv cron > /dev/null 2>&1
echo "   ✅ 系统依赖安装完成"

echo ""
echo "📝 步骤 2/7: 创建用户和目录..."
# 创建专用用户（如果不存在）
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false "$SERVICE_USER"
    echo "   ✅ 创建用户: $SERVICE_USER"
else
    echo "   ℹ️ 用户已存在: $SERVICE_USER"
fi

# 创建目录
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$INSTALL_DIR/logs"
echo "   ✅ 目录创建完成"

echo ""
echo "📝 步骤 3/7: 安装 Python 依赖..."
# 创建虚拟环境
if [ ! -d "$INSTALL_DIR/venv" ]; then
    python3 -m venv "$INSTALL_DIR/venv"
    echo "   ✅ Python 虚拟环境创建完成"
fi

# 激活虚拟环境并安装依赖
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip > /dev/null 2>&1
pip install requests > /dev/null 2>&1
echo "   ✅ Python 依赖安装完成"

echo ""
echo "📝 步骤 4/7: 检查程序文件..."
# 检查必要文件是否存在
if [ ! -f "$INSTALL_DIR/final_email_assistant.py" ]; then
    echo "   ⚠️ 警告: final_email_assistant.py 不存在"
    echo "   请先将程序文件上传到 $INSTALL_DIR"
fi

if [ ! -f "$INSTALL_DIR/daily_summary.py" ]; then
    echo "   ⚠️ 警告: daily_summary.py 不存在"
    echo "   请先将程序文件上传到 $INSTALL_DIR"
fi

if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo "   ⚠️ 警告: config.json 不存在"
    echo "   请先将配置文件上传到 $INSTALL_DIR"
fi
echo "   ✅ 文件检查完成"

echo ""
echo "📝 步骤 5/7: 设置权限..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
chmod +x "$INSTALL_DIR"/*.py 2>/dev/null || true
echo "   ✅ 权限设置完成"

echo ""
echo "📝 步骤 6/7: 创建 Systemd 服务..."

# 创建主服务（23:00 运行）
cat > /etc/systemd/system/email-assistant-main.service << 'EOF'
[Unit]
Description=邮件助手 - 详细版分析
After=network.target

[Service]
Type=oneshot
User=emailbot
Group=emailbot
WorkingDirectory=/opt/email-assistant
ExecStart=/opt/email-assistant/venv/bin/python3 /opt/email-assistant/final_email_assistant.py
StandardOutput=append:/var/log/email-assistant/main.log
StandardError=append:/var/log/email-assistant/main.error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建日报服务（23:30 运行）
cat > /etc/systemd/system/email-assistant-daily.service << 'EOF'
[Unit]
Description=邮件助手 - 每日日报
After=network.target

[Service]
Type=oneshot
User=emailbot
Group=emailbot
WorkingDirectory=/opt/email-assistant
ExecStart=/opt/email-assistant/venv/bin/python3 /opt/email-assistant/daily_summary.py
StandardOutput=append:/var/log/email-assistant/daily.log
StandardError=append:/var/log/email-assistant/daily.error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建定时器（23:00）
cat > /etc/systemd/system/email-assistant-main.timer << 'EOF'
[Unit]
Description=邮件助手 - 每日23:00运行

[Timer]
OnCalendar=*-*-* 23:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 创建定时器（23:30）
cat > /etc/systemd/system/email-assistant-daily.timer << 'EOF'
[Unit]
Description=邮件助手 - 每日23:30运行

[Timer]
OnCalendar=*-*-* 23:30:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 重载 systemd
systemctl daemon-reload
echo "   ✅ Systemd 服务创建完成"

echo ""
echo "📝 步骤 7/7: 启动服务..."
systemctl enable email-assistant-main.timer > /dev/null 2>&1
systemctl enable email-assistant-daily.timer > /dev/null 2>&1
systemctl start email-assistant-main.timer > /dev/null 2>&1
systemctl start email-assistant-daily.timer > /dev/null 2>&1
echo "   ✅ 定时器已启动"

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "📁 安装目录: $INSTALL_DIR"
echo "📊 日志目录: $LOG_DIR"
echo ""
echo "🕐 定时任务:"
echo "   • 23:00 - 详细邮件分析"
echo "   • 23:30 - 今日邮件日报"
echo ""
echo "📋 常用命令:"
echo "   查看定时器状态: systemctl list-timers | grep email"
echo "   查看主服务日志: tail -f /var/log/email-assistant/main.log"
echo "   查看日报日志:   tail -f /var/log/email-assistant/daily.log"
echo "   手动运行主程序: systemctl start email-assistant-main"
echo "   手动运行日报:   systemctl start email-assistant-daily"
echo ""
echo "⚠️  重要提醒:"
echo "   如果程序文件还未上传，请运行上传命令后再测试:"
echo "   scp *.py config.json root@你的服务器IP:$INSTALL_DIR/"
echo ""
