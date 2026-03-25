# 📦 邮件整理助手 - 安装使用指南

## 下载即用版本（推荐）

### 📥 下载

前往 [Releases 页面](https://github.com/AiYuSherry/Email-Organizer-Assistant/releases) 下载对应系统的版本：

| 系统 | 下载文件 | 大小 |
|------|---------|------|
| **macOS** | `Email-Organizer-Assistant-macOS.zip` | ~15MB |
| **Windows** | `Email-Organizer-Assistant-Windows.zip` | ~12MB |
| **Linux** | `Email-Organizer-Assistant-Linux.zip` | ~13MB |

---

## 🍎 macOS 用户使用说明

### 第一步：下载解压

1. 下载 `Email-Organizer-Assistant-macOS.zip`
2. 双击解压，得到 `Email-Organizer-Assistant-macOS` 文件夹

### 第二步：首次配置

1. 打开文件夹，双击 **"点击启动.command"**
2. 首次运行会提示配置：
   - QQ 邮箱地址
   - QQ 邮箱授权码
   - DeepSeek API 密钥

> 💡 **获取授权码**：QQ邮箱 → 设置 → 账户 → 生成授权码  
> 💡 **获取 API 密钥**：[DeepSeek 官网](https://platform.deepseek.com/)

### 第三步：日常使用

配置完成后，以后只需要：
- 双击 **"点击启动.command"**
- 选择 "运行每日摘要" 即可

---

## 🪟 Windows 用户使用说明

### 第一步：下载解压

1. 下载 `Email-Organizer-Assistant-Windows.zip`
2. 右键 → 解压到当前文件夹

### 第二步：首次配置

1. 打开文件夹，双击 **"点击启动.bat"**
2. 首次运行会提示配置相关信息

### 第三步：日常使用

配置完成后，以后只需要：
- 双击 **"点击启动.bat"**
- 选择对应功能即可

---

## 🐧 Linux 用户使用说明

### 第一步：下载解压

```bash
wget https://github.com/AiYuSherry/Email-Organizer-Assistant/releases/download/v1.0/Email-Organizer-Assistant-Linux.zip
unzip Email-Organizer-Assistant-Linux.zip
cd Email-Organizer-Assistant-Linux
```

### 第二步：运行

```bash
./EmailOrganizer-Linux
```

---

## 📝 手动配置方法

如果不想使用图形界面，可以直接编辑配置文件：

1. 打开 `config/config.json.example`
2. 填入你的信息：
```json
{
  "qq_email": "你的邮箱@qq.com",
  "qq_auth_code": "你的授权码",
  "deepseek_key": "你的DeepSeek密钥",
  "imap_server": "imap.qq.com",
  "smtp_server": "smtp.qq.com"
}
```
3. 保存为 `config/config.json`

---

## 🔄 自动化运行

### macOS - 定时运行

1. 打开 "系统偏好设置" → "自动化" → "定时"
2. 或者使用自带的 `setup_auto_run.command`

### Windows - 定时运行

1. 搜索 "任务计划程序"
2. 创建基本任务，设置每天 23:30 运行

---

## ❓ 常见问题

### Q: 提示 "无法打开，因为无法验证开发者" (macOS)

**A:** 前往 系统偏好设置 → 安全性与隐私 → 通用 → 点击"仍要打开"

### Q: 提示缺少 Python

**A:** 下载并安装 Python 3.7+：[python.org/downloads](https://www.python.org/downloads/)

### Q: 邮件发送失败

**A:** 
1. 检查 QQ 授权码是否正确
2. 检查是否开启 IMAP/SMTP 服务
3. 检查网络连接

### Q: DeepSeek API 错误

**A:**
1. 检查 API 密钥是否有效
2. 检查 DeepSeek 账户余额

---

## 📞 需要帮助？

- 查看完整文档：[docs/README.zh-CN.md](./README.zh-CN.md)
- 提交 Issue：[GitHub Issues](https://github.com/AiYuSherry/Email-Organizer-Assistant/issues)

---

**🎉 祝你使用愉快！**
