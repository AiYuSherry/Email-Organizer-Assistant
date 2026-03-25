# 📧 Email Organizer Assistant | 邮件整理助手

<div align="center">

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepSeek AI](https://img.shields.io/badge/AI-DeepSeek-green.svg)](https://deepseek.com/)

**English** | [简体中文](./docs/README.zh-CN.md)

</div>

> 🌐 **Language / 语言**: This document is bilingual (English & 中文). Click above for pure language version.
> <br>本文档为中英双语版本。点击上方切换纯中文版本。

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

## 🚀 Quick Start | 快速开始

### Prerequisites | 前置要求

| Requirement | 需求 |
|-------------|------|
| Python 3.7+ | Python 3.7+ |
| QQ Email account | QQ 邮箱账号 |
| DeepSeek API Key | DeepSeek API 密钥 ([Get here / 在此获取](https://platform.deepseek.com/)) |

### Installation | 安装

```bash
# Clone repository | 克隆仓库
git clone https://github.com/yourusername/Email-Organizer-Assistant.git
cd Email-Organizer-Assistant

# Install dependencies | 安装依赖
pip install -r requirements.txt

# Copy config template | 复制配置模板
cp config/config.json.example config/config.json
```

### Configuration | 配置

Edit `config/config.json`:

```json
{
  "qq_email": "your_email@qq.com / 你的邮箱@qq.com",
  "qq_auth_code": "your_auth_code / 你的授权码",
  "deepseek_key": "your_deepseek_key / 你的DeepSeek密钥",
  "imap_server": "imap.qq.com",
  "smtp_server": "smtp.qq.com"
}
```

> 💡 **Get QQ Auth Code / 获取QQ授权码**: 
> QQ Mail → Settings → Accounts → Generate Authorization Code
> <br>QQ 邮箱 → 设置 → 账户 → 生成授权码

---

## 📖 Usage | 使用方法

### Manual Execution | 手动运行

```bash
# Daily summary | 每日摘要
python src/daily_summary.py

# Detailed analysis | 详细分析
python src/final_email_assistant.py

# Weekly report | 每周报告
python src/weekly_summary.py
```

### Automated Scheduling | 自动运行

#### Option 1: Local (macOS/Linux) | 方式1: 本地运行

```bash
# Daily at 23:30 | 每天 23:30
0 23 * * * /usr/bin/python3 /path/to/src/daily_summary.py
```

#### Option 2: Cloud Server (Recommended) | 方式2: 云服务器 (推荐)

```bash
# Deploy to cloud | 部署到云端
bash scripts/upload_and_deploy.sh
```

📘 **Deployment Guide**: [English](./docs/DEPLOYMENT.md) | [中文](./docs/服务器部署说明.md)

---

## 🏗️ Architecture | 项目结构

```
Email-Organizer-Assistant/
├── src/                          # Source code | 源代码
│   ├── final_email_assistant.py  # Main analysis | 主分析脚本
│   ├── daily_summary.py          # Daily report | 每日摘要
│   ├── weekly_summary.py         # Weekly report | 每周摘要
│   ├── analyze_yesterday.py      # Yesterday analysis | 昨日分析
│   └── config_gui.py             # Config GUI | 配置工具
├── scripts/                      # Deployment scripts | 部署脚本
├── config/                       # Configuration | 配置文件
├── docs/                         # Documentation | 文档
└── logs/                         # Log files | 日志文件
```

---

## 📊 Report Schedule | 报告时间表

| Time | Script | Description | 描述 |
|------|--------|-------------|------|
| 23:00 | `final_email_assistant.py` | Recent emails analysis | 近期邮件分析 |
| 23:30 | `daily_summary.py` | Today's email summary | 今日邮件摘要 |
| Sunday | `weekly_summary.py` | Weekly digest | 每周摘要 |

---

## 📝 Sample Output | 示例输出

### 🇬🇧 Email Report Sections
- 🔴 **Action Required**: Emails requiring attention with deadlines
- ⚪ **Reference Only**: Newsletters and low-priority emails
- 🌐 **Translations**: Automatic translation of English content
- ⏰ **Urgency Labels**: Today/Tomorrow/This week deadlines

### 🇨🇳 邮件报告内容
- 🔴 **需要处理**: 需要你关注的邮件及截止日期
- ⚪ **仅供参考**: 新闻订阅和低优先级邮件
- 🌐 **翻译**: 英文内容自动翻译
- ⏰ **紧急标签**: 今天/明天/本周截止日期

---

## 🛠️ Technology Stack | 技术栈

- **Python 3.7+**: Core language | 核心语言
- **DeepSeek API**: AI analysis and translation | AI 分析和翻译
- **IMAP/SMTP**: Email retrieval and sending | 邮件读取和发送
- **Systemd/Cron**: Task scheduling | 任务调度
- **HTML/CSS**: Email report formatting | 邮件报告格式化

---

## 🤝 Contributing | 贡献

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md).
<br>欢迎贡献！请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

1. Fork the repository | Fork 本仓库
2. Create feature branch | 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. Commit changes | 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch | 推送到分支 (`git push origin feature/AmazingFeature`)
5. Open Pull Request | 打开 Pull Request

---

## 📄 License | 许可证

This project is licensed under the MIT License.
<br>本项目采用 MIT 许可证。

See [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments | 致谢

- [DeepSeek](https://deepseek.com/) for AI API | 提供 AI API
- QQ Mail for IMAP/SMTP support | 提供 IMAP/SMTP 支持

---

## 💡 Tips | 提示

### 🇬🇧 Security & Privacy
- Never commit `config.json` with real credentials
- Code runs locally - emails only sent to DeepSeek API for analysis
- Customize categorization rules in source code

### 🇨🇳 安全与隐私
- 永远不要提交包含真实凭证的 `config.json`
- 代码在本地运行 - 邮件只会发送到 DeepSeek API 进行分析
- 在源代码中自定义分类规则

---

<div align="center">

⭐ Star this repository if you find it helpful! | 如果这个项目对你有帮助，请给它一个 Star！

</div>
