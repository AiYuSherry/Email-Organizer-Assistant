# 📧 Email Organizer Assistant | 邮件整理助手

<div align="center">

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepSeek AI](https://img.shields.io/badge/AI-DeepSeek-green.svg)](https://deepseek.com/)
[![Release](https://img.shields.io/github/v/release/AiYuSherry/Email-Organizer-Assistant)](https://github.com/AiYuSherry/Email-Organizer-Assistant/releases)

**English** | [简体中文](./docs/README.zh-CN.md)

</div>

> 🌐 **Language / 语言**: This document is bilingual (English & 中文). Click above for pure language version.
> <br>本文档为中英双语版本。Click above for pure Chinese version.

---

## 🚀 Quick Start | 快速开始

### ✅ Download & Run (No Python Required) | 下载即用（无需 Python）

| Platform | Download | Size |
|----------|----------|------|
| **🍎 macOS** | [Email-Organizer-Assistant-macOS.zip](https://github.com/AiYuSherry/Email-Organizer-Assistant/releases/latest) | ~15MB |
| **🪟 Windows** | [Email-Organizer-Assistant-Windows.zip](https://github.com/AiYuSherry/Email-Organizer-Assistant/releases/latest) | ~12MB |

**3 Steps to Start:**
1. Download the zip for your system
2. Extract and double-click **"点击启动"** (Start)
3. Follow the prompts to configure

**3步即可使用：**
1. 下载对应系统的 zip 文件
2. 解压后双击 **"点击启动"**
3. 按提示完成配置

📖 **Detailed Guide**: [INSTALL.md](./docs/INSTALL.md) | [安装指南](./docs/INSTALL.md)

---

## ✨ Features | 功能特点

### 🇬🇧 English
- 🤖 **AI-Powered Analysis**: Uses DeepSeek AI to analyze email content and extract key information
- 📊 **Smart Categorization**: Automatically sorts emails into Work, Recruitment, Academic, Admin, Newsletters
- ⏰ **Deadline Detection**: Identifies urgent deadlines and flags them by priority
- 🌐 **Translation**: Automatic translation of English emails to Chinese
- 📱 **Multiple Reports**: Daily Summary, Detailed Analysis, Weekly Report
- ☁️ **Cloud Deployment**: Run on cloud servers for 24/7 operation

### 🇨🇳 中文
- 🤖 **AI 智能分析**: 使用 DeepSeek AI 分析邮件内容并提取关键信息
- 📊 **智能分类**: 自动将邮件分类为工作、招聘、学业、行政、新闻订阅
- ⏰ **截止日期检测**: 识别紧急截止日期并按优先级标记
- 🌐 **自动翻译**: 将英文邮件自动翻译为中文
- 📱 **多种报告**: 每日摘要、详细分析、每周报告
- ☁️ **云端部署**: 在云服务器上 24/7 运行

---

## 📦 Installation | 安装

### Method 1: Download Pre-built Binary (Recommended) | 方式1：下载预编译版本（推荐）

No Python installation required! Just download and run.
<br>无需安装 Python！下载解压后即可运行。

```
📁 Email-Organizer-Assistant-macOS/
├── 📱 Email Organizer Assistant.app  ← macOS App
├── ⚙️ config/config.json.example
├── 📖 docs/
└── 🚀 点击启动.command  ← Double-click to start
```

### Method 2: Source Code | 方式2：源代码运行

For developers who want to customize.
<br>适合需要自定义的开发者。

```bash
# Clone repository | 克隆仓库
git clone https://github.com/AiYuSherry/Email-Organizer-Assistant.git
cd Email-Organizer-Assistant

# Install dependencies | 安装依赖
pip install -r requirements.txt

# Run | 运行
./start_mac.command      # macOS
start_windows.bat        # Windows
```

---

## 🎯 Usage | 使用方法

### First Time Setup | 首次使用

1. **Launch the app** | 启动程序
   - macOS: Double-click `点击启动.command`
   - Windows: Double-click `点击启动.bat`

2. **Configure** | 配置
   - Enter QQ Email | 输入 QQ 邮箱
   - Enter QQ Auth Code | 输入 QQ 授权码
   - Enter DeepSeek API Key | 输入 DeepSeek API 密钥

3. **Run** | 运行
   - Select "Run Daily Summary" | 选择 "运行每日摘要"
   - Check your email! | 查收邮件！

### Daily Use | 日常使用

Just double-click the start script and select the function you need.
<br>双击启动脚本，选择需要的功能即可。

---

## 🏗️ Project Structure | 项目结构

```
Email-Organizer-Assistant/
├── 🚀 点击启动.command      # macOS Launcher
├── 🚀 点击启动.bat          # Windows Launcher
├── 📱 launcher.py           # Main launcher
├── 📁 src/                  # Source code
├── 📁 scripts/              # Deployment scripts
├── 📁 config/               # Configuration
└── 📁 docs/                 # Documentation
```

---

## 📊 Report Schedule | 报告时间表

| Time | Function | Description | 描述 |
|------|----------|-------------|------|
| 23:00 | Full Analysis | Recent emails analysis | 近期邮件分析 |
| 23:30 | Daily Summary | Today's email summary | 今日邮件摘要 |
| Sunday | Weekly Report | Weekly digest | 每周摘要 |

---

## 🛠️ Configuration | 配置

Edit `config/config.json`:

```json
{
  "qq_email": "your_email@qq.com",
  "qq_auth_code": "your_auth_code",
  "deepseek_key": "your_deepseek_key",
  "imap_server": "imap.qq.com",
  "smtp_server": "smtp.qq.com"
}
```

> 💡 **Get QQ Auth Code**: QQ Mail → Settings → Accounts → Generate Authorization Code
> <br>💡 **获取 QQ 授权码**: QQ 邮箱 → 设置 → 账户 → 生成授权码

---

## ☁️ Cloud Deployment | 云端部署

Deploy to a cloud server for 24/7 operation.
<br>部署到云服务器实现 24/7 自动运行。

```bash
bash scripts/upload_and_deploy.sh
```

📘 **Guide**: [DEPLOYMENT.md](./docs/DEPLOYMENT.md) | [部署指南](./docs/服务器部署说明.md)

---

## 🤝 Contributing | 贡献

Contributions are welcome!
<br>欢迎贡献！

See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📄 License | 许可证

MIT License - see [LICENSE](./LICENSE)

---

## 🙏 Acknowledgments | 致谢

- [DeepSeek](https://deepseek.com/) for AI API
- QQ Mail for IMAP/SMTP support

---

<div align="center">

⭐ **Star this repository if you find it helpful!**
<br>⭐ **如果这个项目对你有帮助，请给它一个 Star！**

</div>
