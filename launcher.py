#!/usr/bin/env python3
"""
邮件整理助手 - 启动器
Email Organizer Assistant - Launcher
支持图形界面配置和一键运行
"""

import os
import sys
import json
import subprocess
import platform
from datetime import datetime

# 检测系统类型
SYSTEM = platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'
IS_MAC = SYSTEM == 'Darwin'
IS_WINDOWS = SYSTEM == 'Windows'
IS_LINUX = SYSTEM == 'Linux'

# 获取程序目录
if getattr(sys, 'frozen', False):
    # 打包后的路径
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.json')
SRC_DIR = os.path.join(BASE_DIR, 'src')

def ensure_config_exists():
    """确保配置文件存在"""
    config_dir = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    if not os.path.exists(CONFIG_PATH):
        # 创建默认配置
        default_config = {
            "qq_email": "",
            "qq_auth_code": "",
            "deepseek_key": "",
            "imap_server": "imap.qq.com",
            "smtp_server": "smtp.qq.com"
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return False
    return True

def run_gui_config():
    """运行图形界面配置"""
    config_gui_path = os.path.join(SRC_DIR, 'config_gui.py')
    if os.path.exists(config_gui_path):
        subprocess.run([sys.executable, config_gui_path], cwd=BASE_DIR)
    else:
        print("❌ 找不到配置工具")

def run_daily_summary():
    """运行每日摘要"""
    script_path = os.path.join(SRC_DIR, 'daily_summary.py')
    if os.path.exists(script_path):
        print("📧 正在运行每日邮件摘要...")
        subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    else:
        print("❌ 找不到脚本文件")

def run_full_analysis():
    """运行完整分析"""
    script_path = os.path.join(SRC_DIR, 'final_email_assistant.py')
    if os.path.exists(script_path):
        print("🔍 正在运行完整邮件分析...")
        subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    else:
        print("❌ 找不到脚本文件")

def run_weekly_summary():
    """运行每周摘要"""
    script_path = os.path.join(SRC_DIR, 'weekly_summary.py')
    if os.path.exists(script_path):
        print("📊 正在运行每周邮件摘要...")
        subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    else:
        print("❌ 找不到脚本文件")

def check_requirements():
    """检查依赖是否安装"""
    try:
        import requests
        return True
    except ImportError:
        return False

def install_requirements():
    """安装依赖"""
    req_file = os.path.join(BASE_DIR, 'requirements.txt')
    if os.path.exists(req_file):
        print("📦 正在安装依赖...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file])
        print("✅ 依赖安装完成")

def print_menu():
    """打印菜单"""
    os.system('cls' if IS_WINDOWS else 'clear')
    print("=" * 60)
    print("📧 邮件整理助手 | Email Organizer Assistant")
    print("=" * 60)
    print(f"系统: {SYSTEM} | Python: {platform.python_version()}")
    print("-" * 60)
    print()
    print("请选择操作 / Please select an option:")
    print()
    print("  1. 📝 配置设置 / Configuration")
    print("  2. 📧 运行每日摘要 / Run Daily Summary")
    print("  3. 🔍 运行完整分析 / Run Full Analysis")
    print("  4. 📊 运行每周摘要 / Run Weekly Summary")
    print("  5. 📦 安装依赖 / Install Dependencies")
    print()
    print("  0. 🚪 退出 / Exit")
    print()
    print("-" * 60)

def main():
    """主函数"""
    # 首次运行检查
    is_first_run = not ensure_config_exists()
    
    if is_first_run:
        print("=" * 60)
        print("🎉 欢迎使用邮件整理助手！")
        print("   Welcome to Email Organizer Assistant!")
        print("=" * 60)
        print()
        print("首次使用，请先完成配置 / First time use, please complete configuration")
        print()
        input("按回车键开始配置 / Press Enter to start configuration...")
        run_gui_config()
    
    # 检查依赖
    if not check_requirements():
        print("⚠️ 缺少依赖，请先安装 / Missing dependencies, please install first")
        install = input("是否现在安装？/ Install now? (y/n): ")
        if install.lower() == 'y':
            install_requirements()
    
    while True:
        print_menu()
        choice = input("请输入选项 / Enter option: ").strip()
        
        if choice == '1':
            run_gui_config()
            input("\n按回车键返回菜单 / Press Enter to return to menu...")
        
        elif choice == '2':
            run_daily_summary()
            input("\n按回车键返回菜单 / Press Enter to return to menu...")
        
        elif choice == '3':
            run_full_analysis()
            input("\n按回车键返回菜单 / Press Enter to return to menu...")
        
        elif choice == '4':
            run_weekly_summary()
            input("\n按回车键返回菜单 / Press Enter to return to menu...")
        
        elif choice == '5':
            install_requirements()
            input("\n按回车键返回菜单 / Press Enter to return to menu...")
        
        elif choice == '0':
            print("\n👋 再见！/ Goodbye!")
            break
        
        else:
            print("\n❌ 无效选项 / Invalid option")
            input("按回车键继续 / Press Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！/ Goodbye!")
        sys.exit(0)
