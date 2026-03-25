# 📘 Email Organizer Assistant - Setup Guide

Complete setup guide for the Email Organizer Assistant.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration](#configuration)
3. [First Run](#first-run)
4. [Automated Scheduling](#automated-scheduling)
5. [Cloud Deployment](#cloud-deployment)

---

## Prerequisites

### Required Software

- **Python 3.7 or higher**
  ```bash
  python3 --version
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

### Required Accounts

1. **QQ Email Account**
   - Used for sending and receiving email reports
   - Must enable IMAP/SMTP service

2. **DeepSeek API Key**
   - Used for AI email analysis
   - Get your key at: https://platform.deepseek.com/

---

## Configuration

### Step 1: Copy Configuration Template

```bash
cp config/config.json.example config/config.json
```

### Step 2: Edit Configuration File

Open `config/config.json` and fill in your information:

```json
{
  "qq_email": "your_email@qq.com",
  "qq_auth_code": "your_auth_code_here",
  "deepseek_key": "your_deepseek_api_key_here",
  "imap_server": "imap.qq.com",
  "smtp_server": "smtp.qq.com"
}
```

### Getting Your QQ Auth Code

1. Log in to QQ Mail (mail.qq.com)
2. Go to **Settings** → **Accounts**
3. Find **POP3/IMAP/SMTP** service
4. Click **Generate Authorization Code**
5. Follow the verification steps
6. Copy the generated code

### Getting Your DeepSeek API Key

1. Visit https://platform.deepseek.com/
2. Create an account or log in
3. Go to **API Keys** section
4. Create a new API key
5. Copy the key (save it securely!)

---

## First Run

### Test Configuration

```bash
python src/config_gui.py
```

Or run directly:

```bash
python src/daily_summary.py
```

You should see output like:
```
[2026-03-25 23:30:00] 📧 Email Organizer Assistant - Daily Summary
[2026-03-25 23:30:00] ============================================================
[2026-03-25 23:30:00] 📥 Connecting to QQ Mail...
[2026-03-25 23:30:01]    ✅ Connected successfully
...
[2026-03-25 23:35:00] ✅ Email sent successfully!
```

Check your QQ Mail inbox for the test report.

---

## Automated Scheduling

### macOS (using launchd)

#### Method 1: Using Provided Scripts

```bash
cd "/path/to/Email-Organizer-Assistant"

# Set up daily summary at 23:30
bash setup_auto_run.command
```

#### Method 2: Manual Setup

Create a plist file at `~/Library/LaunchAgents/com.emailassistant.dailysummary.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.emailassistant.dailysummary</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>23</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>/path/to/Email-Organizer-Assistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/Email-Organizer-Assistant/src/daily_summary.py</string>
    </array>
    <key>StandardOutPath</key>
    <string>/path/to/Email-Organizer-Assistant/logs/daily_summary.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/Email-Organizer-Assistant/logs/daily_summary_error.log</string>
</dict>
</plist>
```

Load the plist:

```bash
launchctl load ~/Library/LaunchAgents/com.emailassistant.dailysummary.plist
```

### Linux (using cron)

```bash
# Edit crontab
crontab -e

# Add line for daily summary at 23:30
30 23 * * * /usr/bin/python3 /path/to/Email-Organizer-Assistant/src/daily_summary.py >> /path/to/Email-Organizer-Assistant/logs/daily_summary.log 2>&1
```

### Windows (using Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 23:30
4. Set action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\Email-Organizer-Assistant\src\daily_summary.py`

---

## Cloud Deployment

For 24/7 operation even when your computer is off, deploy to a cloud server.

See detailed guides:
- [English Deployment Guide](./DEPLOYMENT.md)
- [中文部署指南](./服务器部署说明.md)

### Quick Cloud Deploy

```bash
bash scripts/upload_and_deploy.sh
```

---

## 🔧 Troubleshooting

### Issue: "Config file not found"

**Solution**: Ensure `config.json` exists in the project root or `config/` directory.

```bash
ls config/config.json
```

### Issue: "Authentication failed"

**Solution**: 
- Check your QQ Auth Code is correct
- Ensure IMAP/SMTP is enabled in QQ Mail settings
- Verify the auth code hasn't expired

### Issue: "DeepSeek API error"

**Solution**:
- Verify your API key is valid
- Check your DeepSeek account has available credits
- Ensure network connectivity to api.deepseek.com

### Issue: "No emails found"

**Solution**:
- Check if emails are in the inbox (not archived)
- Verify the date range is correct
- Ensure IMAP access is working

---

## 📊 Managing Your Assistant

### View Logs

```bash
# View daily summary logs
tail -f logs/daily_summary.log

# View error logs
tail -f logs/daily_summary_error.log
```

### Stop Automated Tasks

**macOS:**
```bash
launchctl unload ~/Library/LaunchAgents/com.emailassistant.dailysummary.plist
```

**Linux:**
```bash
crontab -e
# Remove the scheduled line
```

---

## ✅ Setup Complete!

Your Email Organizer Assistant is now ready to use!

- **Manual run**: `python src/daily_summary.py`
- **Automated**: Set up scheduled tasks
- **Cloud**: Deployed to server for 24/7 operation

Enjoy your organized inbox! 📧✨
