#!/bin/bash
# 邮件整理助手 - Mac 启动脚本
# Email Organizer Assistant - Mac Launcher

cd "$(dirname "$0")"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3"
    echo "   Python3 not found"
    echo ""
    echo "请先安装 Python 3.7 或更高版本:"
    echo "Please install Python 3.7 or higher first:"
    echo "  https://www.python.org/downloads/"
    echo ""
    read -p "按回车键退出 / Press Enter to exit..."
    exit 1
fi

# 启动程序
echo "🚀 启动邮件整理助手..."
echo "   Starting Email Organizer Assistant..."
echo ""

python3 launcher.py

# 保持窗口打开（如果程序异常退出）
echo ""
read -p "按回车键关闭 / Press Enter to close..."
