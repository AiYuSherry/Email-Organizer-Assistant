# 📧 邮件整理助手 | Email Organizer Assistant

<div align="center">

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepSeek AI](https://img.shields.io/badge/AI-DeepSeek-green.svg)](https://deepseek.com/)

[English](../README.md) | **简体中文**

</div>

> 🌐 **语言 / Language**: 本文档为中文版本。Click [here](../README.md) for English version.

---

## ✨ 功能特点 | Features

- 🤖 **AI 智能分析**: 使用 DeepSeek AI 分析邮件内容并提取关键信息
- 📊 **智能分类**: 自动将邮件分类为工作、招聘、学业、行政、新闻订阅
- ⏰ **截止日期检测**: 识别紧急截止日期并按优先级标记
- 🌐 **自动翻译**: 将英文邮件自动翻译为中文
- 📱 **多种报告类型**:
  - 每日摘要 (23:30)
  - 详细分析 (23:00)
  - 每周报告 (周日)
- ☁️ **云端部署**: 在云服务器上 24/7 运行
- 📧 **邮件投递**: 报告直接发送到你的 QQ 邮箱

---

## 🚀 快速开始

### 前置要求

- Python 3.7+
- QQ 邮箱账号（用于接收报告）
- DeepSeek API 密钥 ([在此获取](https://platform.deepseek.com/))

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/Email-Organizer-Assistant.git
cd Email-Organizer-Assistant

# 安装依赖
pip install -r requirements.txt

# 复制配置模板
cp config/config.json.example config/config.json
```

### 配置应用

```json
{
  "qq_email": "你的邮箱@qq.com",
  "qq_auth_code": "你的QQ授权码",
  "deepseek_key": "你的DeepSeek API密钥",
  "imap_server": "imap.qq.com",
  "smtp_server": "smtp.qq.com"
}
```

> 💡 **获取 QQ 授权码**: 进入 QQ 邮箱 → 设置 → 账户 → 生成授权码

---

## 📖 使用方法

### 手动运行

```bash
# 每日详细分析
python src/daily_summary.py

# 主邮件分析
python src/final_email_assistant.py

# 每周摘要
python src/weekly_summary.py
```

### 自动运行

#### 方式 1: 本地运行 (macOS/Linux)

```bash
# 每天 23:30 运行
0 23 * * * /usr/bin/python3 /path/to/src/daily_summary.py
```

#### 方式 2: 云服务器部署 (推荐)

```bash
# 一键上传并部署
bash scripts/upload_and_deploy.sh
```

📘 **部署指南**: [中文](./服务器部署说明.md) | [English](./DEPLOYMENT.md)

---

## 🏗️ 项目结构

```
Email-Organizer-Assistant/
├── src/                      # 源代码
│   ├── final_email_assistant.py   # 主分析脚本
│   ├── daily_summary.py           # 每日摘要报告
│   ├── weekly_summary.py          # 每周摘要报告
│   ├── analyze_yesterday.py       # 昨日分析
│   └── config_gui.py              # 配置图形界面
├── scripts/                  # 部署脚本
│   ├── deploy.sh            # 服务器部署
│   └── upload_and_deploy.sh # 一键部署
├── config/                   # 配置文件
│   └── config.json.example  # 配置模板
├── docs/                     # 文档
└── logs/                     # 日志文件
```

---

## 📊 报告时间表

| 时间 | 脚本 | 描述 |
|------|------|------|
| 23:00 | `final_email_assistant.py` | 近期邮件详细分析 |
| 23:30 | `daily_summary.py` | 今日邮件摘要 |
| 周日 | `weekly_summary.py` | 每周摘要 |

---

## 📝 示例输出

生成的邮件报告包括：

- 🔴 **需要处理**: 需要你关注的邮件及截止日期
- ⚪ **仅供参考**: 新闻订阅和低优先级邮件
- 🌐 **翻译**: 英文内容自动翻译
- ⏰ **紧急标签**: 今天/明天/本周截止日期

---

## 🛠️ 技术栈

- **Python 3.7+**: 核心语言
- **DeepSeek API**: AI 分析和翻译
- **IMAP/SMTP**: 邮件读取和发送
- **Systemd/Cron**: 任务调度
- **HTML/CSS**: 邮件报告格式化

---

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](../LICENSE) 文件。

---

## 🙏 致谢

- [DeepSeek](https://deepseek.com/) 提供 AI API
- QQ 邮箱提供 IMAP/SMTP 支持

---

## 💡 提示

- **安全**: 永远不要提交包含真实凭证的 `config.json`
- **隐私**: 代码在本地运行 - 你的邮件只会发送到 DeepSeek API 进行分析
- **自定义**: 修改源代码中的分类规则以适应你的需求

---

<div align="center">

⭐ 如果这个项目对你有帮助，请给它一个 Star！

</div>
