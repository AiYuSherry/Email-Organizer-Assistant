# 📧 Email Organizer Assistant - Deployment Guide

This guide explains how to deploy the Email Organizer Assistant to a cloud server for 24/7 automated operation.

---

## 🎯 Overview

Deploy the Email Organizer Assistant to a cloud server (e.g., Baidu Cloud) so it runs continuously, even when your local computer is shut down.

**Target Server**: `120.48.76.86` (Example Baidu Cloud Server)  
**Installation Directory**: `/opt/email-assistant`

---

## ⚡ Quick Deployment (Recommended)

### Method 1: One-Click Script (Easiest)

**Step 1: Ensure SSH Access**

```bash
ssh root@120.48.76.86
```

If you can log in successfully, proceed to the next step.

**Step 2: Run the One-Click Deployment Script**

On your local Mac, open Terminal and run:

```bash
cd "/path/to/Email-Organizer-Assistant"
bash scripts/upload_and_deploy.sh
```

This script will automatically:
- ✅ Upload all necessary files to the server
- ✅ Install Python and dependencies
- ✅ Configure Systemd scheduled tasks
- ✅ Start the services

---

### Method 2: Manual Step-by-Step Deployment

If the one-click script encounters issues, deploy manually:

**Step 1: Upload Files**

On your local Mac Terminal:

```bash
cd "/path/to/Email-Organizer-Assistant"

# Create remote directory
ssh root@120.48.76.86 "mkdir -p /opt/email-assistant"

# Upload files
scp src/final_email_assistant.py root@120.48.76.86:/opt/email-assistant/
scp src/daily_summary.py root@120.48.76.86:/opt/email-assistant/
scp config/config.json root@120.48.76.86:/opt/email-assistant/
scp scripts/deploy.sh root@120.48.76.86:/tmp/
```

**Step 2: Execute Deployment Script on Server**

```bash
ssh root@120.48.76.86
bash /tmp/deploy.sh
```

---

## 🧪 Testing the Deployment

After deployment, test manually:

```bash
# SSH into server
ssh root@120.48.76.86

# Navigate to program directory
cd /opt/email-assistant

# Run daily summary manually for testing
sudo /opt/email-assistant/venv/bin/python3 daily_summary.py
```

If you see:
```
✅ Email sent successfully!
```

Deployment is successful!

---

## 📋 Management & Maintenance

### View Scheduled Task Status

```bash
ssh root@120.48.76.86

# View timer status
systemctl list-timers | grep email

# Expected output:
# email-assistant-daily.timer  email-assistant-daily.service  Tue 2026-03-18 23:30:00 CST
# email-assistant-main.timer   email-assistant-main.service   Tue 2026-03-18 23:00:00 CST
```

### View Logs

```bash
ssh root@120.48.76.86

# Main program logs (runs at 23:00)
tail -f /var/log/email-assistant/main.log

# Daily summary logs (runs at 23:30)
tail -f /var/log/email-assistant/daily.log

# Error logs
tail -f /var/log/email-assistant/main.error.log
tail -f /var/log/email-assistant/daily.error.log
```

### Manual Execution

```bash
ssh root@120.48.76.86

# Run main program manually
systemctl start email-assistant-main

# Run daily summary manually
systemctl start email-assistant-daily
```

### Stop/Restart Services

```bash
ssh root@120.48.76.86

# Stop timers
systemctl stop email-assistant-main.timer
systemctl stop email-assistant-daily.timer

# Restart timers
systemctl restart email-assistant-main.timer
systemctl restart email-assistant-daily.timer

# Disable auto-start
systemctl disable email-assistant-main.timer
systemctl disable email-assistant-daily.timer

# Enable auto-start
systemctl enable email-assistant-main.timer
systemctl enable email-assistant-daily.timer
```

---

## 🔧 Updating the Program

If you modify local files and need to update the server:

```bash
cd "/path/to/Email-Organizer-Assistant"

# Upload updated files
scp src/final_email_assistant.py root@120.48.76.86:/opt/email-assistant/
scp src/daily_summary.py root@120.48.76.86:/opt/email-assistant/

# Restart services (run after SSH login)
ssh root@120.48.76.86 "systemctl restart email-assistant-main.timer email-assistant-daily.timer"
```

---

## 🛠️ Troubleshooting

### Issue 1: Email Sending Fails

**Troubleshooting Steps:**

```bash
ssh root@120.48.76.86

# Check configuration
cat /opt/email-assistant/config.json

# Run program manually to see detailed errors
cd /opt/email-assistant
sudo /opt/email-assistant/venv/bin/python3 daily_summary.py
```

**Common Causes:**
- QQ Email authorization code expired → Regenerate in QQ Mail settings
- Server firewall blocking outbound connections → Check `iptables` or security group settings

### Issue 2: Scheduled Tasks Not Running

**Troubleshooting Steps:**

```bash
ssh root@120.48.76.86

# Check timer status
systemctl status email-assistant-main.timer
systemctl status email-assistant-daily.timer

# Check service status
systemctl status email-assistant-main.service
systemctl status email-assistant-daily.service

# View Systemd logs
journalctl -u email-assistant-main.service -n 50
journalctl -u email-assistant-daily.service -n 50
```

### Issue 3: Program Runs but No Email Received

**Check spam/junk folder:**
- Check QQ Mail spam folder
- Check if emails are auto-sorted to other folders

---

## 📁 File Reference

| File | Description |
|------|-------------|
| `final_email_assistant.py` | Main program - Detailed analysis of recent emails |
| `daily_summary.py` | Daily summary - Analyzes today's emails |
| `config.json` | Configuration file - Contains email and API credentials |
| `deploy.sh` | Server deployment script |
| `upload_and_deploy.sh` | Local one-click upload and deploy script |

---

## ⏰ Schedule

| Time | Program | Function |
|------|---------|----------|
| 23:00 | final_email_assistant.py | Analyze recent emails (detailed) |
| 23:30 | daily_summary.py | Analyze today's emails (daily report) |

---

## ✅ Deployment Checklist

- [ ] Can SSH into server
- [ ] Files uploaded to `/opt/email-assistant/`
- [ ] Manual test successfully sends email
- [ ] Scheduled tasks enabled (`systemctl list-timers` shows them)
- [ ] Log directory writable (`/var/log/email-assistant/`)

---

## 🎉 Done!

After deployment, your Email Organizer Assistant will run 24/7 on the cloud:
- ✅ Daily detailed email analysis at 23:00
- ✅ Daily email summary at 23:30
- ✅ Local computer can be shut down without affecting service

**You can now turn off your computer, the assistant will continue working in the cloud!**

---

For Chinese deployment guide, see [服务器部署说明.md](./服务器部署说明.md)
