#!/bin/bash
# 邮件助手 - 一键上传并部署脚本（在本地 Mac 运行）

# 配置
SERVER_IP="120.48.76.86"  # 你的百度云服务器 IP
SERVER_USER="root"
LOCAL_DIR="/Users/huziyang/Desktop/计算机/邮件助手"
REMOTE_DIR="/opt/email-assistant"

echo "========================================"
echo "📧 邮件助手 - 一键上传并部署"
echo "========================================"
echo ""
echo "🎯 目标服务器: $SERVER_USER@$SERVER_IP"
echo ""

# 检查必要文件
echo "🔍 检查本地文件..."
if [ ! -f "$LOCAL_DIR/final_email_assistant.py" ]; then
    echo "❌ 错误: final_email_assistant.py 不存在"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/daily_summary.py" ]; then
    echo "❌ 错误: daily_summary.py 不存在"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/config.json" ]; then
    echo "❌ 错误: config.json 不存在"
    exit 1
fi
echo "   ✅ 所有文件已就绪"

echo ""
echo "📤 正在上传文件到服务器..."

# 上传主程序
echo "   上传 final_email_assistant.py..."
scp "$LOCAL_DIR/final_email_assistant.py" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

# 上传日报程序
echo "   上传 daily_summary.py..."
scp "$LOCAL_DIR/daily_summary.py" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

# 上传配置
echo "   上传 config.json..."
scp "$LOCAL_DIR/config.json" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

# 上传部署脚本
echo "   上传 deploy.sh..."
scp "$LOCAL_DIR/deploy.sh" "$SERVER_USER@$SERVER_IP:/tmp/"

echo ""
echo "🚀 正在服务器上执行部署..."
ssh "$SERVER_USER@$SERVER_IP" "bash /tmp/deploy.sh"

echo ""
echo "========================================"
echo "✅ 全部完成！"
echo "========================================"
echo ""
echo "🧪 建议测试一下:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cd $REMOTE_DIR"
echo "   sudo /opt/email-assistant/venv/bin/python3 daily_summary.py"
echo ""
