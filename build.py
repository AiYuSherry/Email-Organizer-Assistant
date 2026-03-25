#!/usr/bin/env python3
"""
邮件整理助手 - 构建脚本
自动打包为独立可执行文件
"""

import os
import sys
import platform
import subprocess
import shutil

SYSTEM = platform.system()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
BUILD_DIR = os.path.join(BASE_DIR, 'build')

def clean():
    """清理旧的构建文件"""
    print("🧹 清理旧的构建文件...")
    for dir_path in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"   已删除: {dir_path}")

def check_pyinstaller():
    """检查 PyInstaller 是否安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("📦 安装 PyInstaller...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    print("✅ PyInstaller 安装完成")

def build():
    """构建可执行文件"""
    print(f"🔨 开始构建 ({SYSTEM})...")
    
    # 构建命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'build.spec'
    ]
    
    subprocess.run(cmd, cwd=BASE_DIR, check=True)
    print("✅ 构建完成")

def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    # 确定输出目录
    if SYSTEM == 'Darwin':
        output_name = 'EmailOrganizer-macOS'
        package_name = 'Email-Organizer-Assistant-macOS'
    elif SYSTEM == 'Windows':
        output_name = 'EmailOrganizer-Windows'
        package_name = 'Email-Organizer-Assistant-Windows'
    else:
        output_name = 'EmailOrganizer-Linux'
        package_name = 'Email-Organizer-Assistant-Linux'
    
    # 创建发布目录
    release_dir = os.path.join(BASE_DIR, 'releases', package_name)
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # 复制可执行文件
    exe_path = os.path.join(DIST_DIR, output_name)
    if SYSTEM == 'Windows':
        exe_path += '.exe'
    
    if os.path.exists(exe_path):
        if os.path.isdir(exe_path):  # macOS .app 包
            shutil.copytree(exe_path, os.path.join(release_dir, os.path.basename(exe_path)))
        else:
            shutil.copy2(exe_path, release_dir)
    
    # 复制配置文件模板
    config_example = os.path.join(BASE_DIR, 'config', 'config.json.example')
    config_dir = os.path.join(release_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    shutil.copy2(config_example, os.path.join(config_dir, 'config.json.example'))
    
    # 复制文档
    docs_to_copy = ['README.md', 'LICENSE']
    for doc in docs_to_copy:
        src = os.path.join(BASE_DIR, doc)
        if os.path.exists(src):
            shutil.copy2(src, release_dir)
    
    # 复制说明文档
    docs_dir = os.path.join(BASE_DIR, 'docs')
    if os.path.exists(docs_dir):
        release_docs = os.path.join(release_dir, 'docs')
        os.makedirs(release_docs, exist_ok=True)
        for doc in ['DEPLOYMENT.md', 'FOR_FRIENDS.md', 'SETUP.md', 
                    '服务器部署说明.md', '给朋友的使用说明.md']:
            src = os.path.join(docs_dir, doc)
            if os.path.exists(src):
                shutil.copy2(src, release_docs)
    
    # 创建启动脚本
    if SYSTEM == 'Windows':
        # Windows 启动脚本
        bat_content = '''@echo off
title 邮件整理助手
"%~dp0EmailOrganizer-Windows.exe"
pause
'''
        with open(os.path.join(release_dir, '点击启动.bat'), 'w', encoding='utf-8') as f:
            f.write(bat_content)
    
    elif SYSTEM == 'Darwin':
        # macOS 启动脚本
        sh_content = '''#!/bin/bash
cd "$(dirname "$0")"
open "Email Organizer Assistant.app"
'''
        sh_path = os.path.join(release_dir, '点击启动.command')
        with open(sh_path, 'w') as f:
            f.write(sh_content)
        os.chmod(sh_path, 0o755)
    
    # 创建 ZIP 压缩包
    zip_path = os.path.join(BASE_DIR, 'releases', f'{package_name}.zip')
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    shutil.make_archive(
        os.path.join(BASE_DIR, 'releases', package_name),
        'zip',
        os.path.join(BASE_DIR, 'releases'),
        package_name
    )
    
    print(f"✅ 发布包已创建: {zip_path}")
    return zip_path

def main():
    """主函数"""
    print("=" * 60)
    print("📧 邮件整理助手 - 构建工具")
    print("   Email Organizer Assistant - Build Tool")
    print("=" * 60)
    print()
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        print("⚠️ PyInstaller 未安装")
        install = input("是否安装? / Install? (y/n): ")
        if install.lower() == 'y':
            install_pyinstaller()
        else:
            print("❌ 无法继续构建")
            return
    
    # 清理旧文件
    clean()
    
    # 构建
    try:
        build()
        zip_path = create_release_package()
        print()
        print("=" * 60)
        print("🎉 构建成功！")
        print(f"📦 发布包: {zip_path}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 构建失败: {e}")
        return

if __name__ == '__main__':
    main()
