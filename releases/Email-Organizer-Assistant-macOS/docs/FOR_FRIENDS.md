# 📧 Email Organizer Assistant - For Friends

A simple guide for friends who want to use this email assistant.

---

## 🎁 What is This?

An AI-powered email assistant that:
- Automatically reads your emails
- Uses AI to analyze and categorize them
- Sends you a daily summary report
- Highlights important emails and deadlines

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Python

**macOS:**
```bash
# Python usually comes pre-installed
python3 --version
```

**Windows:**
Download from https://python.org/downloads/

**Linux:**
```bash
sudo apt-get install python3 python3-pip
```

### Step 2: Download the Program

```bash
git clone https://github.com/yourusername/Email-Organizer-Assistant.git
cd Email-Organizer-Assistant
```

Or download the ZIP file and extract it.

### Step 3: Install Dependencies

```bash
pip install requests
```

### Step 4: Configure

1. Copy the config template:
   ```bash
   cp config/config.json.example config/config.json
   ```

2. Edit `config/config.json` with your info:
   ```json
   {
     "qq_email": "your_email@qq.com",
     "qq_auth_code": "your_auth_code",
     "deepseek_key": "your_deepseek_key",
     "imap_server": "imap.qq.com",
     "smtp_server": "smtp.qq.com"
   }
   ```

### Step 5: Get Required Credentials

#### Get QQ Auth Code:
1. Go to mail.qq.com
2. Settings → Accounts
3. Enable IMAP/SMTP service
4. Generate Authorization Code

#### Get DeepSeek API Key:
1. Go to https://platform.deepseek.com/
2. Sign up / Log in
3. Create API Key

### Step 6: Test Run

```bash
python src/daily_summary.py
```

Check your QQ Mail for the test report!

---

## 📅 Set Up Daily Automation

### macOS

```bash
bash setup_auto_run.command
```

### Linux

```bash
crontab -e
# Add this line:
30 23 * * * /usr/bin/python3 /path/to/src/daily_summary.py
```

### Windows

Use Task Scheduler to run `daily_summary.py` daily at 23:30.

---

## ☁️ Cloud Deployment (Optional)

Want it to run even when your computer is off?

```bash
bash scripts/upload_and_deploy.sh
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for details.

---

## 📝 What You'll Receive

Every day at 23:30, you'll get an email with:

### 🔴 Action Required
- Work-related emails
- Job applications / Career opportunities
- Academic matters
- Administrative tasks
- **With deadlines highlighted!**

### ⚪ Reference Only
- Newsletters
- Subscriptions
- Low-priority emails

### ✨ Features
- AI-generated summaries
- Automatic translation of English emails
- Urgency labels (Today/Tomorrow/This week)

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Config not found" | Make sure config.json exists |
| "Auth failed" | Check QQ Auth Code |
| "API error" | Check DeepSeek API key |
| No emails in report | Check if emails are in inbox |

---

## 💡 Tips

- The program runs locally - your data stays private
- Only email metadata is sent to DeepSeek for analysis
- You can customize categories in the source code
- Reports are sent to your own email

---

## 📧 Questions?

Ask the friend who shared this with you!

Or open an issue on GitHub.

---

**Enjoy your organized inbox!** 🎉
