# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件
用于打包邮件整理助手为独立可执行文件
"""

import platform

# 根据系统类型设置输出名称
system = platform.system()
if system == 'Darwin':
    output_name = 'EmailOrganizer-macOS'
    console_app = False  # macOS 可以做成 .app 包
elif system == 'Windows':
    output_name = 'EmailOrganizer-Windows'
    console_app = True   # Windows 保留控制台
else:
    output_name = 'EmailOrganizer-Linux'
    console_app = True

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/*.py', 'src'),
        ('scripts/*.sh', 'scripts'),
        ('config/config.json.example', 'config'),
        ('requirements.txt', '.'),
        ('LICENSE', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=['requests', 'tkinter', 'json', 'imaplib', 'smtplib', 'email'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=output_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console_app,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 暂时不使用自定义图标
    # icon='assets/icon.ico' if system == 'Windows' else 'assets/icon.icns',
)

# macOS 打包为 .app 应用包
if system == 'Darwin':
    app = BUNDLE(
        exe,
        name='Email Organizer Assistant.app',
        # 暂时不使用自定义图标
        # icon='assets/icon.icns',
        bundle_identifier='com.emailorganizer.app',
    )
