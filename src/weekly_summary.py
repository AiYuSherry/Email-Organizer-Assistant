#!/usr/bin/env python3
"""
邮件助手 - 周汇总版（周日晚上运行，汇总一周邮件）
"""
import os
import re
import json
import imaplib
import email
import requests
import smtplib
from datetime import datetime, timedelta, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============== 配置 ==============
QQ_EMAIL = "1515745331@qq.com"
QQ_AUTH_CODE = "qevdfnwpnqjnfeac"
IMAP_SERVER = "imap.qq.com"
IMAP_PORT = 993

# DeepSeek API
DEEPSEEK_API_KEY = "sk-f1a4d30d14f94bf0818a7427d3ce9347"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def decode_header(header):
    if not header:
        return ""
    decoded_parts = email.header.decode_header(header)
    result = ""
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result += part.decode(charset or 'utf-8', errors='ignore')
            except:
                result += part.decode('utf-8', errors='ignore')
        else:
            result += part
    return result

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
                    if content_type == "text/html":
                        body = re.sub(r'<[^>]+>', ' ', body)
                        body = re.sub(r'\s+', ' ', body).strip()
                    break
                except:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='ignore')
        except:
            body = str(msg.get_payload())
    return body

def parse_email_date(date_str):
    """解析邮件日期字符串为 datetime 对象，统一转换为本地时间"""
    if not date_str:
        return None
    
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S',
        '%d %b %Y %H:%M:%S',
    ]
    
    date_str = date_str.split('(')[0].strip()
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                return dt
            # 有时区信息：转换为本地时区
            dt_local = dt.astimezone()
            return dt_local.replace(tzinfo=None)
        except ValueError:
            continue
    
    return None


def get_weekly_emails():
    """获取最近7天（本周一到现在）的所有邮件"""
    print("📥 正在连接 QQ 邮箱，获取本周邮件...")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(QQ_EMAIL, QQ_AUTH_CODE)
        mail.select('inbox')
        
        # 计算本周一和今天的日期
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())  # 本周一
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 搜索从上周六开始的邮件（确保不漏掉邮件），然后本地过滤
        since_date = (monday - timedelta(days=2)).strftime('%d-%b-%Y')
        _, data = mail.search(None, f'SINCE {since_date}')
        email_ids = data[0].split()
        
        if not email_ids:
            print("📭 本周没有新邮件")
            return []
        
        email_ids.reverse()  # 最新的在前
        
        print(f"📊 从服务器获取了 {len(email_ids)} 封邮件，正在筛选本周邮件...")
        
        emails = []
        skipped = 0
        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject = decode_header(msg['Subject'])
            from_addr = decode_header(msg['From'])
            date_str = decode_header(msg['Date'])
            
            # 解析邮件日期并过滤
            email_date = parse_email_date(date_str)
            if email_date:
                if email_date < monday or email_date >= today + timedelta(days=1):
                    skipped += 1
                    continue
            
            body = get_email_body(msg)
            
            emails.append({
                'id': len(emails) + 1,
                'subject': subject,
                'from': from_addr,
                'received': date_str,
                'body': body[:1500]
            })
        
        mail.logout()
        print(f"✅ 成功获取本周 {len(emails)} 封邮件（跳过 {skipped} 封非本周邮件）")
        return emails
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def analyze_weekly_with_deepseek(emails):
    """用 DeepSeek AI 分析一周邮件"""
    if not emails:
        return {"urgent": [], "this_week": [], "reference": [], "translations": {}, "weekly_overview": ""}
    
    # 获取日期范围
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    
    emails_text = []
    for e in emails:
        emails_text.append(f"""【邮件 {e['id']}】
发件人: {e['from']}
主题: {e['subject']}
正文: {e['body'][:600]}
""")
    
    emails_str = '\n---\n'.join(emails_text)
    
    prompt = f"""你是一个邮件助手。本周是 {monday.strftime('%m月%d日')} 至 {(monday + timedelta(days=6)).strftime('%m月%d日')}。请分析这周邮件，按优先级分类。

【分类标准】
🔴 紧急（urgent）- 本周必须处理：
   - 紧急DDL（本周截止）
   - 导师/法院/学校行政紧急通知
   - 需要本周内完成的事项

🟡 重要（this_week）- 近期需关注：
   - 下周DDL
   - 面试、实习、笔试
   - 非紧急学术事务

⚪ 参考（reference）- 仅供参考：
   - 一般通知、公告
   - 已过滤广告后的低价值信息

【输出格式】
- 每封邮件：• [发件人]：[3-4句中文摘要，Who/What/When/Action]
- 时间格式：X月X日（周X）HH:MM
- 🔴类必须提供完整信息（时间地点行动要求）
- 🟡⚪类一句话中文摘要
- 禁止废话，每句一个信息点

邮件列表：
{emails_str}

返回严格的 JSON 格式：
{{
    "weekly_overview": "这周邮件整体情况（2-3句话）",
    "urgent": [
        {{
            "id": 邮件编号,
            "sender": "发件人名称",
            "summary": "中文摘要",
            "deadline": "截止时间",
            "action_required": "行动要求",
            "is_english": true/false
        }}
    ],
    "this_week": [
        {{
            "id": 邮件编号,
            "sender": "发件人名称",
            "summary": "中文摘要",
            "deadline": "截止时间",
            "is_english": true/false
        }}
    ],
    "reference": [
        {{
            "id": 邮件编号,
            "sender": "发件人名称",
            "summary": "一句话摘要",
            "is_english": true/false
        }}
    ],
    "translations": {{
        "1": "邮件1的中文翻译",
        "2": "..."
    }}
}}

重要规则：
- 促销、广告、娱乐放入reference或忽略
- 导师、法院、DDL紧急的放入urgent
- 面试、实习、笔试放入urgent或this_week
- 只返回JSON"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的邮件助手"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    try:
        print("🤖 正在使用 DeepSeek AI 分析本周邮件...")
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=120)
        result = resp.json()
        
        if 'error' in result:
            print(f"API 错误: {result['error']}")
            return {"task_emails": [], "translations": {}, "summaries": {}, "weekly_overview": "分析失败"}
        
        content = result['choices'][0]['message']['content']
        
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]
        
        parsed = json.loads(content.strip())
        urgent_count = len(parsed.get('urgent', []))
        week_count = len(parsed.get('this_week', []))
        print(f"✅ 分析完成，发现 🔴{urgent_count} 紧急 🟡{week_count} 本周")
        return parsed
        
    except Exception as e:
        print(f"分析失败: {e}")
        return {"urgent": [], "this_week": [], "reference": [], "translations": {}, "weekly_overview": "分析出错"}

def generate_weekly_html(emails, analysis):
    """生成周汇总 HTML 报告"""
    urgent = analysis.get('urgent', [])
    this_week = analysis.get('this_week', [])
    reference = analysis.get('reference', [])
    translations = analysis.get('translations', {})
    overview = analysis.get('weekly_overview', '')
    
    # 计算日期范围
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    date_range_str = f"{monday.strftime('%m月%d日')}-{sunday.strftime('%m月%d日')}"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; max-width: 800px; margin: 0 auto; padding: 15px; line-height: 1.6; color: #333; font-size: 14px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; }}
        .overview {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196F3; font-size: 14px; }}
        
        .section-urgent {{ background: #ffebee; border-left: 5px solid #f44336; padding: 12px 15px; margin: 25px 0 15px; border-radius: 4px; }}
        .section-urgent h2 {{ margin: 0; color: #c62828; font-size: 16px; }}
        
        .section-week {{ background: #fff8e1; border-left: 5px solid #ffc107; padding: 12px 15px; margin: 25px 0 15px; border-radius: 4px; }}
        .section-week h2 {{ margin: 0; color: #f57c00; font-size: 16px; }}
        
        .section-ref {{ background: #f5f5f5; border-left: 5px solid #9e9e9e; padding: 12px 15px; margin: 25px 0 15px; border-radius: 4px; }}
        .section-ref h2 {{ margin: 0; color: #616161; font-size: 16px; }}
        
        .email-list {{ list-style: none; padding: 0; margin: 0; }}
        .email-item {{ background: white; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 12px; padding: 15px; }}
        .email-item.urgent {{ border-left: 4px solid #f44336; }}
        .email-item.week {{ border-left: 4px solid #ffc107; }}
        .email-item.ref {{ border-left: 4px solid #9e9e9e; }}
        
        .email-sender {{ font-weight: bold; color: #333; margin-bottom: 6px; }}
        .email-summary {{ color: #444; line-height: 1.7; }}
        .email-deadline {{ color: #d32f2f; font-weight: bold; margin-top: 8px; }}
        .email-action {{ color: #1565c0; margin-top: 6px; }}
        
        details {{ margin-top: 12px; }}
        summary {{ cursor: pointer; color: #667eea; font-size: 13px; padding: 8px 12px; background: #f5f5f5; border-radius: 6px; display: inline-block; }}
        summary:hover {{ background: #e8e8e8; }}
        
        .detail-box {{ margin-top: 12px; padding: 15px; background: #fafafa; border-radius: 6px; border: 1px solid #e0e0e0; }}
        .translation-section {{ margin-bottom: 15px; }}
        .translation-section h4 {{ margin: 0 0 8px 0; color: #2196F3; font-size: 13px; }}
        .translation-content {{ background: #e3f2fd; padding: 12px; border-radius: 4px; white-space: pre-wrap; font-size: 13px; }}
        .original-section h4 {{ margin: 0 0 8px 0; color: #666; font-size: 13px; }}
        .original-content {{ background: white; padding: 12px; border-radius: 4px; border: 1px solid #ddd; white-space: pre-wrap; font-size: 13px; max-height: 400px; overflow-y: auto; }}
        
        .week-badge {{ display: inline-block; background: #ff9800; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-left: 10px; }}
        .empty-msg {{ color: #999; font-style: italic; padding: 15px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 本周邮件汇总 <span class="week-badge">周报</span></h1>
        <p>统计周期：{date_range_str} | 共 {len(emails)} 封 | 🔴{len(urgent)} 紧急 🟡{len(this_week)} 重要</p>
    </div>
    
    <div class="overview">
        <strong>📊 周概览：</strong>{overview}
    </div>
"""
    
    # 🔴 紧急
    html += '<div class="section-urgent"><h2>🔴 本周紧急（必须处理）</h2></div>'
    if urgent:
        html += '<ul class="email-list">'
        for item in urgent:
            html += render_weekly_email_item(item, 'urgent', emails, translations)
        html += '</ul>'
    else:
        html += '<div class="empty-msg">暂无紧急事项 ✓</div>'
    
    # 🟡 本周重要
    html += '<div class="section-week"><h2>🟡 本周重要（需关注）</h2></div>'
    if this_week:
        html += '<ul class="email-list">'
        for item in this_week:
            html += render_weekly_email_item(item, 'week', emails, translations)
        html += '</ul>'
    else:
        html += '<div class="empty-msg">暂无本周重要事项</div>'
    
    # ⚪ 参考
    html += '<div class="section-ref"><h2>⚪ 仅供参考</h2></div>'
    if reference:
        html += '<ul class="email-list">'
        for item in reference:
            html += render_weekly_email_item(item, 'ref', emails, translations)
        html += '</ul>'
    else:
        html += '<div class="empty-msg">无其他邮件</div>'
    
    html += "</body></html>"
    return html

def render_weekly_email_item(item, level, emails, translations):
    """渲染周汇总邮件项"""
    sender = escape_html(item.get('sender', '未知发件人'))
    summary = item.get('summary', '').replace('\n', '<br>')
    deadline = item.get('deadline', '')
    action = item.get('action_required', '')
    is_english = item.get('is_english', False)
    email_id = item.get('id', 0)
    
    # 查找邮件原文
    email = next((e for e in emails if e['id'] == email_id), None)
    translation = translations.get(str(email_id), '')
    
    deadline_html = f'<div class="email-deadline">⏰ 截止时间：{escape_html(deadline)}</div>' if deadline else ''
    action_html = f'<div class="email-action">✓ 行动：{escape_html(action)}</div>' if action else ''
    
    # 展开详情
    detail_html = ''
    if email:
        body_clean = escape_html(email.get('body', '')[:1500])
        if is_english and translation and level in ['urgent', 'week']:
            detail_html = f'''
            <details>
                <summary>📋 点击展开中英文全文</summary>
                <div class="detail-box">
                    <div class="translation-section">
                        <h4>中文翻译：</h4>
                        <div class="translation-content">{escape_html(translation)}</div>
                    </div>
                    <div class="original-section">
                        <h4>英文原文：</h4>
                        <div class="original-content">{body_clean}</div>
                    </div>
                </div>
            </details>'''
        elif level == 'urgent':
            detail_html = f'''
            <details>
                <summary>📋 点击展开原文</summary>
                <div class="detail-box">
                    <div class="original-section">
                        <h4>邮件原文：</h4>
                        <div class="original-content">{body_clean}</div>
                    </div>
                </div>
            </details>'''
    
    return f"""<li class="email-item {level}">
    <div class="email-sender">• {sender}：</div>
    <div class="email-summary">{summary}</div>
    {deadline_html}
    {action_html}
    {detail_html}
</li>
"""


def escape_html(text):
    """转义 HTML 特殊字符"""
    if not text:
        return ''
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def send_email(subject, html_content):
    msg = MIMEMultipart()
    msg['From'] = QQ_EMAIL
    msg['To'] = QQ_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login(QQ_EMAIL, QQ_AUTH_CODE)
        server.send_message(msg)
    print(f"✅ 周汇总已发送至 {QQ_EMAIL}")

def main():
    print("="*60)
    print("📧 本周邮件汇总启动 (DeepSeek AI 版)")
    print("="*60)
    
    # 获取本周邮件（最多50封）
    print("\n📥 从 QQ 邮箱获取本周邮件...")
    emails = get_weekly_emails()
    
    if not emails:
        print("\n📭 本周没有新邮件")
        return
    
    # AI 分析
    print("\n🧠 使用 DeepSeek AI 生成本周汇总...")
    analysis = analyze_weekly_with_deepseek(emails)
    urgent_count = len(analysis.get('urgent', []))
    week_count = len(analysis.get('this_week', []))
    
    # 生成周汇总
    print("\n📊 生成本周汇总报告...")
    html = generate_weekly_html(emails, analysis)
    
    # 发送
    today = datetime.now()
    week_num = today.isocalendar()[1]
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    date_range = f"{monday.strftime('%m月%d日')}-{sunday.strftime('%m月%d日')}"
    send_email(f"📊 第{week_num}周邮件汇总 [{date_range}] - 🔴{urgent_count} 紧急 🟡{week_count} 重要", html)
    
    print("\n✅ 周汇总完成！请检查 QQ 邮箱")
    print(f"💰 本周汇总消耗约 {task_count * 0.03:.2f} 元")

if __name__ == "__main__":
    main()
