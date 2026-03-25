#!/bin/bash
# GitHub 初始化脚本
# 使用方法: bash github-init.sh

echo "========================================"
echo "🚀 Email Organizer Assistant - GitHub 初始化"
echo "========================================"
echo ""

# 检查 git 是否安装
if ! command -v git &> /dev/null; then
    echo "❌ 请先安装 Git"
    exit 1
fi

# 初始化 git 仓库
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git branch -M main
else
    echo "✅ Git 仓库已存在"
fi

# 添加文件
echo "📁 添加文件到仓库..."
git add .

# 首次提交
echo "💾 创建首次提交..."
git commit -m "Initial commit: Email Organizer Assistant

Features:
- AI-powered email analysis with DeepSeek
- Daily/weekly email summaries
- Smart categorization
- Automatic translation
- Cloud deployment support

Includes:
- Source code
- Deployment scripts
- Documentation (English & Chinese)
- MIT License"

echo ""
echo "========================================"
echo "✅ 初始化完成！"
echo "========================================"
echo ""
echo "下一步操作:"
echo "1. 在 GitHub 创建新仓库"
echo "2. 运行以下命令推送到 GitHub:"
echo ""
echo "   git remote add origin https://github.com/你的用户名/Email-Organizer-Assistant.git"
echo "   git push -u origin main"
echo ""
echo "或者使用 SSH:"
echo "   git remote add origin git@github.com:你的用户名/Email-Organizer-Assistant.git"
echo "   git push -u origin main"
echo ""
