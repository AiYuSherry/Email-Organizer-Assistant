@echo off
chcp 65001 >nul
title 邮件整理助手 | Email Organizer Assistant

REM 切换到脚本所在目录
cd /d "%~dp0"

echo ========================================
echo 📧 邮件整理助手 | Email Organizer Assistant
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python
    echo    Python not found
    echo.
    echo 请先安装 Python 3.7 或更高版本:
    echo Please install Python 3.7 or higher first:
    echo   https://www.python.org/downloads/
    echo   安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python 已检测到 | Python detected
echo.
echo 🚀 启动程序... | Starting program...
echo.

python launcher.py

REM 保持窗口打开
echo.
pause
