#!/usr/bin/env python3
"""
邮件助手 - 分析昨天（3月17日）的邮件（一次性脚本）
"""
import os
import re
import json
import imaplib
import email
import requests
import smtplib
import socket
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 设置全局 socket 超时（防止网络阻塞）
socket.setdefaulttimeout(30)

# ============== 配置 ==============
if getattr(sys, 'frozen', False):
    CONFIG_PATH = os.path.join(os.path.dirname(sys.executable), 'config.json')
else:
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"❌ 找不到配置文件: {CONFIG_PATH}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"❌ 配置文件格式错误")
    sys.exit(1)

QQ_EMAIL = config.get('qq_email', '')
QQ_AUTH_CODE = config.get('qq_auth_code', '')
IMAP_SERVER = config.get('imap_server', 'imap.qq.com')
SMTP_SERVER = config.get('smtp_server', 'smtp.qq.com')
IMAP_PORT = 993
SMTP_PORT = 465

DEEPSEEK_API_KEY = config.get('deepseek_key', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

if not all([QQ_EMAIL, QQ_AUTH_CODE, DEEPSEEK_API_KEY]):
    print("❌ 配置不完整，请检查 config.json 文件")
    sys.exit(1)

# ============== 目标日期配置 ==============
# 分析昨天（3月17日）的邮件
TARGET_DATE = datetime(2026, 3, 17)  # 2026年3月17日

def log_message(msg):
    """打印并记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(log_line)

def decode_header(header):
    """解码邮件头"""
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
    """获取邮件正文"""
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
    """解析邮件日期字符串为 datetime 对象"""
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
            dt_local = dt.astimezone()
            return dt_local.replace(tzinfo=None)
        except ValueError:
            continue
    
    return None

def get_yesterday_emails():
    """获取昨天（3月17日）的所有邮件"""
    log_message("📥 正在连接 QQ 邮箱，获取昨天（3月17日）的邮件...")
    log_message(f"   服务器: {IMAP_SERVER}:{IMAP_PORT}")
    log_message(f"   账号: {QQ_EMAIL[:5]}...")
    
    mail = None
    try:
        log_message("   正在建立 SSL 连接...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=30)
        log_message("   ✅ SSL 连接成功")
        
        log_message("   正在登录...")
        mail.login(QQ_EMAIL, QQ_AUTH_CODE)
        log_message("   ✅ 登录成功")
        
        mail.select('inbox')
        log_message("   ✅ 选择收件箱")
        
        # 计算昨天的时间范围
        yesterday_start = TARGET_DATE.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday_start + timedelta(days=1)
        yesterday_str_imap = TARGET_DATE.strftime('%d-%b-%Y')
        
        log_message(f"   搜索日期: {yesterday_str_imap} ({TARGET_DATE.strftime('%Y年%m月%d日')})")
        log_message(f"   时间范围: {yesterday_start} 至 {yesterday_end}")
        
        # 使用 IMAP 搜索昨天的邮件
        _, messages = mail.search(None, f'(ON "{yesterday_str_imap}")')
        msg_ids = messages[0].split()
        log_message(f"   IMAP 找到 {len(msg_ids)} 封该日期邮件")
        
        # 限制处理数量
        max_emails = 50
        check_limit = min(len(msg_ids), 150)
        msg_ids_to_check = msg_ids[-check_limit:] if len(msg_ids) > check_limit else msg_ids
        
        log_message(f"   将检查 {len(msg_ids_to_check)} 封邮件...")
        
        email_list = []
        
        for i, num in enumerate(msg_ids_to_check):
            if len(email_list) >= max_emails:
                log_message(f"   已达到最大处理数量 {max_emails}，停止")
                break
                
            if (i + 1) % 10 == 0 or i == 0 or i == len(msg_ids_to_check) - 1:
                log_message(f"   检查中... {i+1}/{len(msg_ids_to_check)} (已确认 {len(email_list)} 封)")
            
            try:
                _, msg_data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                date_str = msg.get('Date', '')
                email_date = parse_email_date(date_str)
                
                # 只保留昨天的邮件
                if email_date and yesterday_start <= email_date < yesterday_end:
                    subject = decode_header(msg.get('Subject', ''))
                    sender = decode_header(msg.get('From', ''))
                    body = get_email_body(msg)
                    
                    # 清理发件人
                    sender_clean = re.sub(r'<[^>]+>', '', sender).strip()
                    sender_clean = sender_clean.strip('"').strip("'")
                    if len(sender_clean) < 5:
                        match = re.search(r'@([^.]+)', sender)
                        if match:
                            sender_clean = match.group(1)
                        else:
                            sender_clean = sender
                    if not sender_clean:
                        sender_clean = "未知发件人"
                    if len(sender_clean) > 100:
                        sender_clean = sender_clean[:100] + "..."
                    
                    email_list.append({
                        'id': len(email_list) + 1,
                        'subject': subject,
                        'sender': sender_clean,
                        'body': body[:2000],
                        'date': email_date.strftime('%H:%M'),
                        'full_date': email_date
                    })
                    
                    log_message(f"      ✅ 找到: [{sender_clean[:30]}...] {subject[:40]}...")
                    
            except Exception as e:
                log_message(f"   ⚠️ 处理邮件出错: {e}")
                continue
        
        if mail:
            try:
                mail.close()
                mail.logout()
            except:
                pass
        
        log_message(f"✅ 最终获取到 {len(email_list)} 封昨天（3月17日）的邮件")
        return email_list
        
    except Exception as e:
        log_message(f"❌ 邮箱连接失败: {e}")
        if mail:
            try:
                mail.close()
                mail.logout()
            except:
                pass
        return []

def analyze_emails(emails):
    """使用 DeepSeek AI 详细分析邮件"""
    if not emails:
        return {"work": [], "recruitment": [], "academic": [], "admin": [], "others": [],
                "newsletter": [], "subscription": [], "other_ref": [], "translations": {}}
    
    log_message(f"🤖 正在使用 DeepSeek AI 分析 {len(emails)} 封邮件...")
    
    yesterday_str = TARGET_DATE.strftime('%Y年%m月%d日')
    
    # 构建邮件文本
    emails_text = []
    for e in emails:
        body_limit = 1500 if len(emails) <= 15 else 800
        emails_text.append(f"""【邮件 {e['id']}】
发件人: {e['sender']}
主题: {e['subject']}
时间: {e['date']}
正文: {e['body'][:body_limit]}
""")
    
    emails_str = '\n---\n'.join(emails_text)
    
    prompt = f"""【绝对禁令】严禁编造任何邮件内容！必须100%基于下面提供的真实邮件。

你是一个邮件助手。正在分析 {yesterday_str} 的邮件。

【待分析的邮件内容】
{emails_str}

【分析要求】
1. 仔细阅读上面每封邮件的完整内容
2. 提取所有关键信息：链接、截止时间、地点、操作步骤
3. 对每封邮件进行分类（work/recruitment/academic/admin/others/newsletter/subscription/other_ref）
4. 判断是否为英文邮件（is_english字段）
5. 提取 deadline 并判断紧急度（today/tomorrow/this_week/next_week/none）

【分类规则】
- work: 个人工作沟通、任务分配
- recruitment: 公开招聘、活动报名、职业讲座、实习机会
- academic: 学业事务、课程相关、考试通知
- admin: 行政手续、签证、注册、缴费
- others: 其他需处理事项
- newsletter: 新闻资讯、周报月报
- subscription: 订阅续期、账单
- other_ref: 其他低价值邮件

【输出要求】
- summary必须包含：链接、时间、地点、具体操作步骤
- 不要写"详见邮件"，必须提取具体内容
- 所有英文邮件必须提供translations（正文完整翻译）
- deadline格式：YYYY-MM-DD 或 "无"
- ddl_urgency: today/tomorrow/this_week/next_week/none

返回JSON格式：
{{
    "work": [{{"id": 1, "sender": "...", "full_subject": "...", "subject_cn": "...", "summary": "...", "deadline": "...", "action": "...", "ddl_urgency": "...", "is_english": true/false}}],
    "recruitment": [],
    "academic": [],
    "admin": [],
    "others": [],
    "newsletter": [],
    "subscription": [],
    "other_ref": [],
    "translations": {{"1": "翻译内容...", "2": "..."}}
}}"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个邮件分析助手。基于用户提供的邮件内容进行分析，提取关键信息（链接、DDL、地点、操作步骤），生成中文摘要。对于英文邮件，提供完整中文翻译。返回JSON格式。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 8000,
        "seed": 42
    }
    
    try:
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=120)
        result = resp.json()
        
        if 'error' in result:
            log_message(f"⚠️ API 错误: {result['error']}")
            return create_fallback_result(emails)
        
        content = result['choices'][0]['message']['content']
        
        # 提取 JSON
        json_str = None
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            parts = content.split('```')
            if len(parts) >= 3:
                json_str = parts[1].strip()
        else:
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = content[start:end+1]
        
        if not json_str:
            log_message("⚠️ 无法从响应中提取 JSON")
            return create_fallback_result(emails)
        
        # 清理并修复 JSON
        json_str = json_str.replace('\n\n', '\n').strip()
        if not json_str.rstrip().endswith('}'):
            last_brace = json_str.rfind('}')
            if last_brace > 0:
                json_str = json_str[:last_brace+1]
        
        parsed = json.loads(json_str)
        
        # 验证 ID 并补充缺失的字段
        valid_ids = {e['id'] for e in emails}
        email_dict = {e['id']: e for e in emails}
        
        for category in ['work', 'recruitment', 'academic', 'admin', 'others', 'newsletter', 'subscription', 'other_ref']:
            if category in parsed:
                valid_items = []
                for item in parsed[category]:
                    if item.get('id') in valid_ids:
                        if not item.get('sender'):
                            item['sender'] = email_dict[item['id']].get('sender', '未知发件人')
                        if not item.get('summary') or '请查看邮件' in item.get('summary', ''):
                            item['summary'] = f"来自 {item['sender']} 的邮件，主题：{item.get('full_subject', '无主题')}"
                        valid_items.append(item)
                parsed[category] = valid_items
        
        if 'translations' in parsed:
            parsed['translations'] = {k: v for k, v in parsed['translations'].items() if int(k) in valid_ids}
        
        # 去重
        seen_ids = set()
        for category in ['work', 'recruitment', 'academic', 'admin', 'others', 'newsletter', 'subscription', 'other_ref']:
            if category in parsed:
                unique_items = []
                for item in parsed[category]:
                    if item.get('id') not in seen_ids:
                        seen_ids.add(item['id'])
                        unique_items.append(item)
                parsed[category] = unique_items
        
        total_action = sum(len(parsed.get(k, [])) for k in ['work', 'recruitment', 'academic', 'admin', 'others'])
        total_ref = sum(len(parsed.get(k, [])) for k in ['newsletter', 'subscription', 'other_ref'])
        log_message(f"✅ AI 分析完成：🔴{total_action} 需处理 | ⚪{total_ref} 参考")
        return parsed
        
    except Exception as e:
        log_message(f"⚠️ AI 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return create_fallback_result(emails)

def create_fallback_result(emails):
    """AI 失败时的降级处理"""
    result = {
        "work": [], "recruitment": [], "academic": [], "admin": [], "others": [],
        "newsletter": [], "subscription": [], "other_ref": [], "translations": {}
    }
    
    for e in emails:
        sender = e.get('sender', '').strip()
        if not sender:
            sender = "未知发件人"
        
        email_info = {
            "id": e['id'],
            "sender": sender,
            "full_subject": e.get('subject', '无主题'),
            "subject_cn": "",
            "summary": "【AI分析失败】邮件内容请查看原文",
            "deadline": "",
            "action": "",
            "ddl_urgency": "none",
            "is_english": not any(ord(c) > 127 for c in e.get('subject', ''))
        }
        
        subject_lower = e.get('subject', '').lower()
        from_lower = sender.lower()
        
        if 'news' in subject_lower or 'digest' in subject_lower or 'summary' in subject_lower:
            result["newsletter"].append(email_info)
        elif any(kw in from_lower for kw in ['career', 'job', 'recruit', 'vcrc', 'law']):
            result["recruitment"].append(email_info)
        elif any(kw in subject_lower for kw in ['course', 'class', 'lecture', 'exam']):
            result["academic"].append(email_info)
        else:
            result["others"].append(email_info)
    
    log_message(f"✅ 降级处理：已分类 {len(emails)} 封邮件")
    return result

def sort_by_urgency(items):
    """按DDL紧急度排序"""
    order = {'today': 0, 'tomorrow': 1, 'this_week': 2, 'next_week': 3, 'none': 4, '': 4}
    return sorted(items, key=lambda x: order.get(x.get('ddl_urgency', ''), 4))

def generate_html(emails, analysis):
    """生成详细的 HTML 报告"""
    work = sort_by_urgency(analysis.get('work', []))
    recruitment = sort_by_urgency(analysis.get('recruitment', []))
    academic = sort_by_urgency(analysis.get('academic', []))
    admin = sort_by_urgency(analysis.get('admin', []))
    others = sort_by_urgency(analysis.get('others', []))
    newsletter = analysis.get('newsletter', [])
    subscription = analysis.get('subscription', [])
    other_ref = analysis.get('other_ref', [])
    translations = analysis.get('translations', {})
    
    email_dict = {e['id']: e for e in emails}
    
    total_action = len(work) + len(recruitment) + len(academic) + len(admin) + len(others)
    total_ref = len(newsletter) + len(subscription) + len(other_ref)
    yesterday_str = TARGET_DATE.strftime('%Y年%m月%d日')
    
    def render_email_item(item, category_class):
        eid = item.get('id')
        email_data = email_dict.get(eid, {})
        translation = translations.get(str(eid), '')
        is_english = item.get('is_english', False)
        
        sender = item.get('sender', '').strip() or email_data.get('sender', '未知发件人')
        full_subject = item.get('full_subject', '').strip() or email_data.get('subject', '无主题')
        subject_cn = item.get('subject_cn', '').strip()
        summary = item.get('summary', '').strip()
        deadline = item.get('deadline', '').strip()
        action = item.get('action', '').strip()
        
        urgency = item.get('ddl_urgency', 'none')
        urgency_label = {
            'today': '<span style="color:#d32f2f;font-weight:bold">[今天截止]</span>',
            'tomorrow': '<span style="color:#f57c00;font-weight:bold">[明天截止]</span>',
            'this_week': '<span style="color:#f9a825">[本周截止]</span>',
            'next_week': '<span style="color:#7cb342">[下周]</span>'
        }.get(urgency, '')
        
        html = f'''
        <div class="email-item {category_class}">
            <div class="email-sender">{sender} {urgency_label}</div>
            <div style="color:#666;font-size:13px;margin-bottom:8px;">
                <b>主题：</b>{full_subject}
                {f"<br><b>中文：</b>{subject_cn}" if subject_cn and subject_cn != full_subject else ""}
            </div>
            <div class="email-summary">{summary or "暂无摘要"}</div>
            {f'<div class="email-deadline">⏰ 截止时间：{deadline}</div>' if deadline else ''}
            {f'<div class="email-action">✅ 操作：{action}</div>' if action else ''}
        '''
        
        if is_english and translation:
            html += f'''
            <details>
                <summary>📖 查看英文原文翻译</summary>
                <div class="detail-box">
                    <div class="translation-content">{translation}</div>
                </div>
            </details>
            '''
        
        html += '</div>'
        return html
    
    def render_section(title, items, category_class, icon="📧"):
        if not items:
            return ""
        html = f'<div class="sub-section"><h3>{icon} {title} ({len(items)}封)</h3></div>\n'
        for item in items:
            html += render_email_item(item, category_class)
        return html
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>昨日邮件分析 - {yesterday_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; font-size: 14px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0; font-size: 26px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 15px; }}
        
        .section-action {{ background: #ffebee; border-left: 5px solid #f44336; padding: 15px 20px; margin: 30px 0 20px; border-radius: 8px; }}
        .section-action h2 {{ margin: 0; color: #c62828; font-size: 20px; }}
        
        .sub-section {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px 18px; margin: 25px 0 15px; border-radius: 6px; }}
        .sub-section h3 {{ margin: 0; color: #e65100; font-size: 16px; font-weight: bold; }}
        
        .section-ref {{ background: #f5f5f5; border-left: 5px solid #9e9e9e; padding: 15px 20px; margin: 30px 0 20px; border-radius: 8px; }}
        .section-ref h2 {{ margin: 0; color: #616161; font-size: 20px; }}
        
        .email-item {{ background: white; border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 15px; padding: 18px; border-left: 4px solid #ff9800; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .email-item.work {{ border-left-color: #f44336; }}
        .email-item.academic {{ border-left-color: #2196F3; }}
        .email-item.admin {{ border-left-color: #9c27b0; }}
        .email-item.events {{ border-left-color: #4caf50; }}
        .email-item.ref {{ border-left-color: #9e9e9e; background: #fafafa; }}
        
        .email-sender {{ font-weight: bold; color: #333; margin-bottom: 8px; font-size: 15px; }}
        .email-summary {{ color: #444; line-height: 1.8; margin-top: 10px; }}
        .email-summary b {{ color: #1565c0; }}
        .email-deadline {{ color: #d32f2f; font-weight: bold; margin-top: 10px; padding: 8px 12px; background: #ffebee; border-radius: 6px; display: inline-block; }}
        .email-action {{ color: #2e7d32; margin-top: 10px; padding: 8px 12px; background: #e8f5e9; border-radius: 6px; }}
        
        details {{ margin-top: 15px; }}
        summary {{ cursor: pointer; color: #667eea; font-size: 13px; padding: 10px 15px; background: #f5f5f5; border-radius: 6px; display: inline-block; user-select: none; }}
        summary:hover {{ background: #e8e8e8; }}
        .detail-box {{ margin-top: 15px; padding: 18px; background: #fafafa; border-radius: 8px; border: 1px solid #e0e0e0; }}
        .translation-section {{ margin-bottom: 15px; }}
        .translation-section h4 {{ margin: 0 0 10px 0; color: #2196F3; font-size: 14px; }}
        .translation-content {{ background: #e3f2fd; padding: 15px; border-radius: 6px; line-height: 1.8; }}
        
        .footer {{ margin-top: 40px; padding: 20px; background: #f5f5f5; border-radius: 8px; text-align: center; color: #666; font-size: 13px; }}
        .note {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: #2e7d32; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 昨日邮件分析</h1>
        <p>{yesterday_str} | 共处理 {len(emails)} 封邮件 | 🔴需处理 {total_action} 封 | ⚪参考 {total_ref} 封</p>
    </div>
    
    <div class="note">
        <b>📌 注意：</b>这是针对昨天（{yesterday_str}）邮件的一次性分析报告。
    </div>
'''
    
    # 需要处理的部分
    if total_action > 0:
        html += '<div class="section-action"><h2>🔴 需要处理</h2></div>\n'
        html += render_section('工作相关', work, 'work', '💼')
        html += render_section('招聘/活动', recruitment, 'events', '🎯')
        html += render_section('学业事务', academic, 'academic', '📚')
        html += render_section('行政手续', admin, 'admin', '📋')
        html += render_section('其他事项', others, 'work', '📌')
    
    # 仅供参考的部分
    if total_ref > 0:
        html += '<div class="section-ref"><h2>⚪ 仅供参考</h2></div>\n'
        html += render_section('新闻资讯', newsletter, 'ref', '📰')
        html += render_section('订阅续期', subscription, 'ref', '💳')
        html += render_section('其他低价值', other_ref, 'ref', '🗑️')
    
    # 如果没有邮件
    if total_action == 0 and total_ref == 0:
        html += '''
        <div style="text-align:center;padding:60px 20px;color:#666;">
            <div style="font-size:48px;margin-bottom:20px;">📭</div>
            <div style="font-size:18px;">昨天没有收到新邮件</div>
            <div style="font-size:14px;margin-top:10px;opacity:0.7;">享受这宁静的一天吧 ☕</div>
        </div>
        '''
    
    html += f'''
    <div class="footer">
        <p>📧 此邮件由邮件助手生成（昨日补发） | ⏰ 发送时间：{datetime.now().strftime('%H:%M')}</p>
        <p style="margin-top:8px;opacity:0.7;">🔴 需处理邮件请及时查看 | 灰色邮件可快速浏览</p>
    </div>
</body>
</html>'''
    
    return html

def send_email(html_content, email_count):
    """发送邮件"""
    yesterday_str = TARGET_DATE.strftime('%Y年%m月%d日')
    log_message(f"📤 正在发送 {yesterday_str} 的邮件分析报告...")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = QQ_EMAIL
        msg['To'] = QQ_EMAIL
        msg['Subject'] = f"📧 昨日邮件分析 - {yesterday_str}（{email_count}封）【补发】"
        
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.login(QQ_EMAIL, QQ_AUTH_CODE)
        server.sendmail(QQ_EMAIL, QQ_EMAIL, msg.as_string())
        server.quit()
        
        log_message("✅ 昨日邮件分析报告已发送！")
        return True
        
    except Exception as e:
        log_message(f"❌ 发送邮件失败: {e}")
        return False

def main():
    """主函数"""
    yesterday_str = TARGET_DATE.strftime('%Y年%m月%d日')
    log_message("=" * 60)
    log_message(f"📧 邮件助手 - 分析昨天（{yesterday_str}）的邮件")
    log_message("=" * 60)
    
    # 获取昨天邮件
    emails = get_yesterday_emails()
    
    if not emails:
        # 没有邮件也发送一个空报告
        html = generate_html([], {})
        send_email(html, 0)
        log_message("✅ 昨日无邮件，已发送空报告")
        return
    
    # AI 分析邮件
    analysis = analyze_emails(emails)
    
    # 生成 HTML 报告
    html = generate_html(emails, analysis)
    
    # 发送邮件
    send_email(html, len(emails))
    
    log_message("=" * 60)
    log_message("✅ 昨日邮件分析任务完成")
    log_message("=" * 60)

if __name__ == "__main__":
    main()
