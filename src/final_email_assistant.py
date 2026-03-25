#!/usr/bin/env python3
"""
邮件助手 - DeepSeek AI 版（支持翻译+摘要+任务识别）
"""
import os
import re
import json
import imaplib
import email
import requests
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============== 配置 ==============
import sys

# 获取配置文件路径（如果是打包后的app，在app同目录）
if getattr(sys, 'frozen', False):
    # 打包后的exe/app
    CONFIG_PATH = os.path.join(os.path.dirname(sys.executable), 'config.json')
else:
    # 开发环境
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

# 读取配置
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"❌ 找不到配置文件: {CONFIG_PATH}")
    print("请确保 config.json 文件在同一目录下")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"❌ 配置文件格式错误，请检查 JSON 格式")
    sys.exit(1)

QQ_EMAIL = config.get('qq_email', '')
QQ_AUTH_CODE = config.get('qq_auth_code', '')
IMAP_SERVER = "imap.qq.com"
IMAP_PORT = 993

# DeepSeek API
DEEPSEEK_API_KEY = config.get('deepseek_key', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# 验证配置
if not all([QQ_EMAIL, QQ_AUTH_CODE, DEEPSEEK_API_KEY]):
    print("❌ 配置不完整，请检查 config.json 文件")
    print("需要填写: qq_email, qq_auth_code, deepseek_key")
    sys.exit(1)

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
    """解析邮件日期字符串为 datetime 对象，使用标准库方法"""
    if not date_str:
        return None
    
    try:
        # 使用 email.utils.parsedate_tz - 这是Python标准库专门解析邮件日期的函数
        from email.utils import parsedate_tz, mktime_tz
        
        parsed = parsedate_tz(date_str)
        if parsed:
            # mktime_tz 会处理时区，返回UTC时间戳
            timestamp = mktime_tz(parsed)
            dt = datetime.fromtimestamp(timestamp)
            
            # 验证日期合理性
            if dt.year < 2024 or dt.year > 2030:
                print(f"⚠️ 日期超出合理范围: {date_str} -> {dt}")
                return None
            
            return dt
    except Exception as e:
        # 备用方案：手动解析
        pass
    
    # 备用：手动尝试常见格式
    import re
    date_str_clean = re.sub(r'\s*\([A-Z]+\)\s*$', '', date_str).strip()
    
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',      # Fri, 13 Feb 2026 14:30:00 +0800
        '%d %b %Y %H:%M:%S %z',          # 13 Feb 2026 14:30:00 +0800
        '%a, %d %b %Y %H:%M:%S',         # Fri, 13 Feb 2026 14:30:00
        '%d %b %Y %H:%M:%S',             # 13 Feb 2026 14:30:00
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str_clean, fmt)
            if 2024 <= dt.year <= 2030:
                return dt
        except ValueError:
            continue
    
    print(f"⚠️ 无法解析日期: '{date_str[:80]}'")
    return None


def get_today_emails(max_check=50):
    """从 QQ 邮箱获取当天的邮件（按日期倒序，本地筛选）"""
    print("📥 正在连接 QQ 邮箱...")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(QQ_EMAIL, QQ_AUTH_CODE)
        mail.select('inbox')
        
        # 获取所有邮件ID（QQ邮箱IMAP返回的是按时间升序排列的）
        _, data = mail.search(None, 'ALL')
        all_ids = data[0].split()
        
        if not all_ids:
            print("📭 邮箱中没有邮件")
            return []
        
        print(f"📊 邮箱共 {len(all_ids)} 封邮件")
        
        # 从最新的开始检查（取最后max_check个，然后倒序）
        check_ids = all_ids[-max_check:] if len(all_ids) > max_check else all_ids
        check_ids = list(reversed(check_ids))  # 最新的在前
        
        # 今天的日期范围
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        print(f"🗓️ 今天日期: {now.strftime('%Y-%m-%d %H:%M')}")
        print(f"🔍 筛选范围: {today_start} 至 {today_end}")
        
        # 先获取所有邮件的头部信息（不下载完整内容）
        print(f"\n📋 正在获取最近 {len(check_ids)} 封邮件信息...")
        
        email_candidates = []
        for idx, e_id in enumerate(check_ids[:20]):  # 先检查前20封最新的
            try:
                # 只获取头部信息
                _, msg_data = mail.fetch(e_id, '(BODY.PEEK[HEADER.FIELDS (DATE SUBJECT FROM)])')
                header_bytes = msg_data[0][1]
                
                # 解析头部
                msg = email.message_from_bytes(header_bytes)
                subject = decode_header(msg['Subject']) or "(无主题)"
                from_addr = decode_header(msg['From']) or "(未知发件人)"
                date_str = decode_header(msg['Date']) or ""
                
                # 解析日期
                email_date = parse_email_date(date_str)
                
                print(f"\n  邮件 {idx+1} (ID:{e_id.decode()}):")
                print(f"    发件人: {from_addr[:50]}")
                print(f"    主题: {subject[:60]}")
                print(f"    原始日期: {date_str[:60] if date_str else '无'}")
                print(f"    解析日期: {email_date.strftime('%Y-%m-%d %H:%M') if email_date else '解析失败'}")
                
                if email_date:
                    # 检查是否是今天的
                    is_today = today_start <= email_date < today_end
                    print(f"    是否今天: {'✅ 是' if is_today else '❌ 否'}")
                    
                    if is_today:
                        email_candidates.append({
                            'id': e_id,
                            'subject': subject,
                            'from': from_addr,
                            'date_str': date_str,
                            'date': email_date
                        })
                else:
                    print(f"    ⚠️ 日期解析失败，跳过")
                    
            except Exception as e:
                print(f"    ❌ 获取失败: {e}")
                continue
        
        # 下载今天的完整邮件内容
        print(f"\n📥 下载今天的 {len(email_candidates)} 封邮件内容...")
        emails = []
        for cand in email_candidates:
            try:
                _, msg_data = mail.fetch(cand['id'], '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                body = get_email_body(msg)
                
                emails.append({
                    'id': len(emails) + 1,
                    'subject': cand['subject'],
                    'from': cand['from'],
                    'received': cand['date_str'],
                    'body': body[:2000]
                })
                print(f"  ✅ 已下载: [{cand['subject'][:50]}...]")
            except Exception as e:
                print(f"  ❌ 下载失败: {e}")
        
        mail.logout()
        
        print(f"\n✅ 最终获取今天 {len(emails)} 封邮件")
        
        # 调试：保存邮件内容到文件，方便排查
        debug_file = f"/tmp/email_debug_{now.strftime('%H%M%S')}.txt"
        with open(debug_file, 'w', encoding='utf-8') as f:
            for e in emails:
                f.write(f"【邮件 {e['id']}】\n")
                f.write(f"发件人: {e['from']}\n")
                f.write(f"主题: {e['subject']}\n")
                f.write(f"正文前500字: {e['body'][:500]}\n")
                f.write("-" * 50 + "\n")
        print(f"🐛 调试文件已保存: {debug_file}")
        
        return emails
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def should_filter_email(subject, body, sender):
    """根据关键词判断是否应该过滤掉这封邮件"""
    text = (subject + " " + body + " " + sender).lower()
    
    # 只过滤明显的广告/促销邮件
    filter_keywords = ['广告', '优惠']
    
    for keyword in filter_keywords:
        if keyword in text:
            return True, f"包含过滤词：{keyword}"
    
    return False, None


def analyze_with_deepseek(emails):
    """用 DeepSeek AI 分析邮件"""
    if not emails:
        return {
            "work": [], "recruitment": [], "academic": [], 
            "admin": [], "others": [],
            "newsletter": [], "subscription": [], "other_ref": [],
            "translations": {}
        }
    
    # 获取今天的日期
    today = datetime.now()
    today_str = today.strftime("%Y年%m月%d日")
    tomorrow_str = (today + timedelta(days=1)).strftime("%m月%d日")
    
    # 先过滤邮件
    filtered_emails = []
    skipped_emails = []
    for e in emails:
        should_filter, reason = should_filter_email(e['subject'], e['body'], e['from'])
        if should_filter:
            skipped_emails.append((e['id'], e['subject'][:50], reason))
        else:
            filtered_emails.append(e)
    
    if skipped_emails:
        print(f"🗑️ 已过滤 {len(skipped_emails)} 封邮件：")
        for eid, subj, reason in skipped_emails[:5]:
            print(f"   - 邮件{eid}: {subj}... ({reason})")
        if len(skipped_emails) > 5:
            print(f"   ... 还有 {len(skipped_emails)-5} 封")
    
    if not filtered_emails:
        print("📭 过滤后没有需要处理的邮件")
        return {
            "work": [], "recruitment": [], "academic": [], 
            "admin": [], "others": [],
            "newsletter": [], "subscription": [], "other_ref": [],
            "translations": {}
        }
    
    emails_text = []
    for e in filtered_emails:
        # 限制每封邮件的正文长度，避免token超限
        # 如果邮件太多，进一步缩短
        body_limit = 1500 if len(filtered_emails) <= 10 else 800
        emails_text.append(f"""【邮件 {e['id']}】
发件人: {e['from']}
主题: {e['subject']}
正文: {e['body'][:body_limit]}
""")
    
    emails_str = '\n---\n'.join(emails_text)
    
    # 构建邮件ID映射，用于提示
    id_mapping = "\n".join([f"邮件 {e['id']}: {e['from'][:40]} - {e['subject'][:50]}" for e in filtered_emails])
    
    prompt = f"""【绝对禁令】严禁编造任何邮件内容！必须100%基于下面提供的真实邮件。

你是一个邮件助手。今天是{today_str}。

【待分析的邮件内容】
{emails_str}

【分析要求】
1. 仔细阅读上面每封邮件的完整内容
2. 提取所有关键信息：链接、截止时间、地点、操作步骤
3. 对每封邮件进行分类（work/recruitment/academic/admin/others/newsletter/subscription/other_ref）
4. 判断是否为英文邮件（is_english字段）

【分类规则】
- work: 个人工作沟通
- recruitment: 公开招聘、活动报名、职业讲座  
- academic: 学业事务
- admin: 行政手续
- others: 其他需处理事项
- newsletter: 新闻资讯
- subscription: 订阅续期
- other_ref: 其他低价值

【输出要求】
- summary必须包含：链接、时间、地点、具体操作
- 不要写"详见邮件"，必须提取具体内容
- 所有英文邮件必须提供translations（正文完整翻译）

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
        "temperature": 0.0,  # 降到0减少随机性
        "max_tokens": 8000,  # 增加token上限，防止JSON被截断
        "seed": 42  # 固定seed确保可重复
    }
    
    try:
        print("🤖 正在使用 DeepSeek AI 分析...")
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=120)
        result = resp.json()
        
        if 'error' in result:
            print(f"API 错误: {result['error']}")
            return {"task_emails": [], "translations": {}, "summaries": {}}
        
        content = result['choices'][0]['message']['content']
        
        # 调试：显示AI返回的内容片段
        print(f"📝 AI返回内容片段: {content[:300]}...")
        
        # 提取 JSON - 尝试多种方式
        json_str = None
        
        # 方式1: 找 ```json 代码块
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0].strip()
        # 方式2: 找 ``` 代码块
        elif '```' in content:
            parts = content.split('```')
            if len(parts) >= 3:
                json_str = parts[1].strip()
        # 方式3: 直接找 JSON 对象（大括号包裹的内容）
        else:
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = content[start:end+1]
        
        if not json_str:
            print(f"⚠️ 无法从响应中提取 JSON")
            print(f"响应内容: {content[:500]}...")
            raise ValueError("无法提取 JSON")
        
        # 清理可能的非法字符
        json_str = json_str.replace('\n\n', '\n').strip()
        
        # 检查 JSON 是否被截断（以未闭合的字符串结尾）
        # 如果最后一个非空白字符不是 }，说明被截断了
        if not json_str.rstrip().endswith('}'):
            print(f"⚠️ AI 返回的 JSON 被截断，尝试修复...")
            # 尝试找到最后一个完整的对象并闭合
            last_brace = json_str.rfind('}')
            if last_brace > 0:
                json_str = json_str[:last_brace+1]
                # 尝试补全 translations 字段（如果是这里被截断）
                if json_str.count('{') > json_str.count('}'):
                    json_str += '}' * (json_str.count('{') - json_str.count('}'))
            else:
                print("❌ JSON 截断严重，无法修复")
                raise ValueError("JSON 被截断")
        
        parsed = json.loads(json_str)
        
        # 调试：显示translations情况
        translations = parsed.get('translations', {})
        if translations:
            print(f"📚 AI返回了 {len(translations)} 封邮件的翻译")
        else:
            print(f"⚠️ AI没有返回translations字段")
        
        # 【验证步骤】确保AI返回的邮件ID都在原始邮件列表中
        valid_ids = {e['id'] for e in filtered_emails}
        removed_count = 0
        
        for category in ['work', 'recruitment', 'academic', 'admin', 'others', 'newsletter', 'subscription', 'other_ref']:
            if category in parsed:
                original_count = len(parsed[category])
                # 只保留ID有效的邮件
                parsed[category] = [item for item in parsed[category] if item.get('id') in valid_ids]
                removed_count += original_count - len(parsed[category])
        
        # 验证translations中的ID
        if 'translations' in parsed:
            parsed['translations'] = {k: v for k, v in parsed['translations'].items() if int(k) in valid_ids}
        
        if removed_count > 0:
            print(f"⚠️ 过滤掉 {removed_count} 封AI编造的邮件（ID不存在）")
        
        total_action = sum(len(parsed.get(k, [])) for k in ['work', 'recruitment', 'academic', 'admin', 'others'])
        total_ref = sum(len(parsed.get(k, [])) for k in ['newsletter', 'subscription', 'other_ref'])
        print(f"✅ 分析完成：🔴{total_action} 需处理 | ⚪{total_ref} 参考")
        return parsed
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 降级处理：返回原始邮件信息，确保用户至少能看到邮件
        print("⚠️ 使用降级方案：返回原始邮件列表...")
        fallback_result = {
            "work": [], "recruitment": [], "academic": [], 
            "admin": [], "others": [],
            "newsletter": [], "subscription": [], "other_ref": [],
            "translations": {}
        }
        
        # 将邮件简单分类放入 others（需要处理）和 other_ref（参考）
        for e in filtered_emails:
            email_info = {
                "id": e['id'],
                "sender": e['from'],
                "full_subject": e['subject'],
                "subject_cn": e['subject'] if not any(ord(c) > 127 for c in e['subject']) else "",
                "summary": f"【AI分析失败，显示原文】{e['body'][:500]}...",
                "deadline": "",
                "action": "请手动查看邮件",
                "ddl_urgency": "none",
                "is_english": not any(ord(c) > 127 for c in e['subject'])
            }
            # 简单判断：如果是 newsletter/recruitment 相关发件人，放入对应分类
            subject_lower = e['subject'].lower()
            from_lower = e['from'].lower()
            
            if 'news' in subject_lower or 'digest' in subject_lower or 'summary' in subject_lower:
                fallback_result["newsletter"].append(email_info)
            elif any(kw in from_lower for kw in ['career', 'job', 'recruit', 'vcrc']):
                fallback_result["recruitment"].append(email_info)
            else:
                fallback_result["others"].append(email_info)
        
        print(f"✅ 降级方案：已返回 {len(filtered_emails)} 封原始邮件")
        return fallback_result

def sort_by_urgency(items):
    """按DDL紧急度排序：今天>明天>本周>下周>无DDL"""
    order = {'today': 0, 'tomorrow': 1, 'this_week': 2, 'next_week': 3, 'none': 4, '': 4}
    return sorted(items, key=lambda x: order.get(x.get('ddl_urgency', ''), 4))


def generate_html(emails, analysis):
    """生成 HTML 报告"""
    # 获取各类邮件
    work = sort_by_urgency(analysis.get('work', []))
    recruitment = sort_by_urgency(analysis.get('recruitment', []))
    academic = sort_by_urgency(analysis.get('academic', []))
    admin = sort_by_urgency(analysis.get('admin', []))
    others = sort_by_urgency(analysis.get('others', []))
    newsletter = analysis.get('newsletter', [])
    subscription = analysis.get('subscription', [])
    other_ref = analysis.get('other_ref', [])
    translations = analysis.get('translations', {})
    
    # 获取邮件内容字典
    email_dict = {e['id']: e for e in emails}
    
    # 统计
    total_action = len(work) + len(recruitment) + len(academic) + len(admin) + len(others)
    total_ref = len(newsletter) + len(subscription) + len(other_ref)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>邮件日报 - {datetime.now().strftime('%m月%d日')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; max-width: 850px; margin: 0 auto; padding: 15px; line-height: 1.6; color: #333; font-size: 14px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; }}
        
        /* 🔴 需要处理的大标题 */
        .section-action {{ background: #ffebee; border-left: 5px solid #f44336; padding: 12px 15px; margin: 30px 0 20px; border-radius: 4px; }}
        .section-action h2 {{ margin: 0; color: #c62828; font-size: 18px; }}
        
        /* 子分类标题 */
        .sub-section {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 10px 15px; margin: 25px 0 15px; }}
        .sub-section h3 {{ margin: 0; color: #e65100; font-size: 15px; font-weight: bold; }}
        
        /* ⚪ 仅供参考 */
        .section-ref {{ background: #f5f5f5; border-left: 5px solid #9e9e9e; padding: 12px 15px; margin: 30px 0 20px; border-radius: 4px; }}
        .section-ref h2 {{ margin: 0; color: #616161; font-size: 18px; }}
        
        /* 邮件列表 */
        .email-list {{ list-style: none; padding: 0; margin: 0; }}
        .email-item {{ 
            background: white; 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            margin-bottom: 12px; 
            padding: 15px;
            border-left: 4px solid #ff9800;
        }}
        .email-item.work {{ border-left-color: #f44336; }}
        .email-item.academic {{ border-left-color: #2196F3; }}
        .email-item.admin {{ border-left-color: #9c27b0; }}
        .email-item.events {{ border-left-color: #4caf50; }}
        .email-item.ref {{ border-left-color: #9e9e9e; background: #fafafa; }}
        
        .email-sender {{ font-weight: bold; color: #333; margin-bottom: 6px; }}
        .email-summary {{ color: #444; line-height: 1.8; }}
        .email-deadline {{ color: #d32f2f; font-weight: bold; margin-top: 8px; }}
        .email-action {{ color: #1565c0; margin-top: 6px; }}
        .email-location {{ color: #00695c; margin-top: 6px; }}
        .email-materials {{ color: #5d4037; margin-top: 6px; font-size: 13px; }}
        .mandatory-tag {{ color: #d32f2f; font-weight: bold; }}
        .optional-tag {{ color: #388e3c; }}
        
        details {{ margin-top: 12px; }}
        summary {{ 
            cursor: pointer; 
            color: #667eea; 
            font-size: 13px; 
            padding: 8px 12px; 
            background: #f5f5f5; 
            border-radius: 6px; 
            display: inline-block;
            user-select: none;
        }}
        summary:hover {{ background: #e8e8e8; }}
        
        .detail-box {{ 
            margin-top: 12px; 
            padding: 15px; 
            background: #fafafa; 
            border-radius: 6px; 
            border: 1px solid #e0e0e0;
        }}
        .translation-section {{ margin-bottom: 15px; }}
        .translation-section h4 {{ margin: 0 0 8px 0; color: #2196F3; font-size: 13px; }}
        .translation-content {{ 
            background: #e3f2fd; 
            padding: 12px; 
            border-radius: 4px; 
            white-space: pre-wrap;
            font-size: 13px;
            line-height: 1.7;
        }}
        .original-section h4 {{ margin: 0 0 8px 0; color: #666; font-size: 13px; }}
        .original-content {{ 
            background: white; 
            padding: 12px; 
            border-radius: 4px; 
            border: 1px solid #ddd;
            white-space: pre-wrap;
            font-size: 13px;
            line-height: 1.7;
            max-height: 500px;
            overflow-y: auto;
        }}
        
        .empty-msg {{ color: #999; font-style: italic; padding: 15px; text-align: center; }}
        .urgency-today {{ background: #ffebee; padding: 2px 6px; border-radius: 4px; color: #c62828; font-size: 12px; font-weight: bold; }}
        .urgency-tomorrow {{ background: #fff3e0; padding: 2px 6px; border-radius: 4px; color: #e65100; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 邮件日报</h1>
        <p>{datetime.now().strftime('%Y年%m月%d日')} | 🔴{total_action} 需处理 | ⚪{total_ref} 参考</p>
    </div>
"""
    
    # 🔴 需要处理的
    if total_action > 0:
        html += '<div class="section-action"><h2>🔴 需要处理的</h2></div>'
        
        # 【工作事务】
        if work:
            html += '<div class="sub-section"><h3>【工作事务】</h3></div>'
            html += '<ul class="email-list">'
            for item in work:
                html += render_work_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
            html += '</ul>'
        
        # 【招聘机会】
        if recruitment:
            html += '<div class="sub-section"><h3>【招聘机会】</h3></div>'
            html += '<ul class="email-list">'
            for item in recruitment:
                html += render_recruitment_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
            html += '</ul>'
        
        # 【学业事务】
        if academic:
            html += '<div class="sub-section"><h3>【学业事务】</h3></div>'
            html += '<ul class="email-list">'
            for item in academic:
                html += render_academic_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
            html += '</ul>'
        
        # 【行政手续】
        if admin:
            html += '<div class="sub-section"><h3>【行政手续】</h3></div>'
            html += '<ul class="email-list">'
            for item in admin:
                html += render_admin_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
            html += '</ul>'
        
        # 【其他】
        if others:
            html += '<div class="sub-section"><h3>【其他】</h3></div>'
            html += '<ul class="email-list">'
            for item in others:
                html += render_others_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
            html += '</ul>'
    else:
        html += '<div class="section-action"><h2>🔴 需要处理的</h2></div>'
        html += '<div class="empty-msg">✓ 今天没有需要处理的事项</div>'
    
    # ⚪ 仅供参考
    html += '<div class="section-ref"><h2>⚪ 仅供参考</h2></div>'
    
    if newsletter:
        html += '<div class="sub-section"><h3>【Newsletter/资讯】</h3></div>'
        html += '<ul class="email-list">'
        for item in newsletter:
            html += render_newsletter_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
        html += '</ul>'
    
    if subscription:
        html += '<div class="sub-section"><h3>【订阅续期】</h3></div>'
        html += '<ul class="email-list">'
        for item in subscription:
            html += render_subscription_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
        html += '</ul>'
    
    if other_ref:
        html += '<div class="sub-section"><h3>【其他低价值】</h3></div>'
        html += '<ul class="email-list">'
        for item in other_ref:
            html += render_other_ref_email(item, email_dict.get(item['id']), translations.get(str(item['id']), ''))
        html += '</ul>'
    
    if not any([newsletter, subscription, other_ref]):
        html += '<div class="empty-msg">无参考内容</div>'
    
    html += "</body></html>"
    return html


def render_work_email(item, email, translation):
    """渲染工作事务邮件 - 必须提供中英对照"""
    sender = escape_html(item.get('sender', '未知发件人'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    summary = item.get('summary', '').replace('\n', '<br>')
    deadline = item.get('deadline', '')
    action = item.get('action', '')
    urgency = item.get('ddl_urgency', '')
    is_english = item.get('is_english', False)
    
    urgency_tag = ''
    if urgency == 'today':
        urgency_tag = ' <span class="urgency-today">【今天截止】</span>'
    elif urgency == 'tomorrow':
        urgency_tag = ' <span class="urgency-tomorrow">【明天截止】</span>'
    
    # 构建标题显示：英文邮件显示双语标题，中文邮件只显示原标题
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    deadline_html = f'<div class="email-deadline">⏰ 截止时间：{escape_html(deadline)}</div>' if deadline else ''
    action_html = f'<div class="email-action">✓ 行动：{escape_html(action)}</div>' if action else ''
    
    # 工作邮件必须提供中英对照
    detail_html = ''
    if email:
        body_clean = escape_html(email.get('body', '')[:2000])
        if translation:
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
        else:
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
    
    return f"""<li class="email-item work">
    <div class="email-sender">• {sender}：{urgency_tag}</div>
    {subject_display}
    <div class="email-summary">{summary}</div>
    {deadline_html}
    {action_html}
    {detail_html}
</li>
"""


def render_recruitment_email(item, email, translation):
    """渲染招聘机会邮件 - 必须提供中英对照"""
    sender = escape_html(item.get('sender', '未知发件人'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    summary = item.get('summary', '').replace('\n', '<br>')
    deadline = item.get('deadline', '')
    action = item.get('action', '')
    urgency = item.get('ddl_urgency', '')
    is_english = item.get('is_english', False)
    
    urgency_tag = ''
    if urgency == 'today':
        urgency_tag = ' <span class="urgency-today">【今天截止】</span>'
    elif urgency == 'tomorrow':
        urgency_tag = ' <span class="urgency-tomorrow">【明天截止】</span>'
    
    # 构建标题显示
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    deadline_html = f'<div class="email-deadline">📅 申请截止：{escape_html(deadline)}</div>' if deadline else ''
    action_html = f'<div class="email-action">✓ 行动：{escape_html(action)}</div>' if action else ''
    
    # 招聘邮件必须提供中英对照
    detail_html = ''
    if email:
        body_clean = escape_html(email.get('body', '')[:2000])
        if translation:
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
        else:
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
    
    return f"""<li class="email-item">
    <div class="email-sender">• {sender}：{urgency_tag}</div>
    {subject_display}
    <div class="email-summary">{summary}</div>
    {deadline_html}
    {action_html}
    {detail_html}
</li>
"""


def render_academic_email(item, email, translation):
    """渲染学业事务邮件 - 带DDL的提供中英对照"""
    sender = escape_html(item.get('sender', '未知发件人'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    summary = item.get('summary', '').replace('\n', '<br>')
    deadline = item.get('deadline', '')
    action = item.get('action', '')
    has_ddl = item.get('has_deadline', False)
    urgency = item.get('ddl_urgency', '')
    is_english = item.get('is_english', False)
    
    urgency_tag = ''
    if urgency == 'today':
        urgency_tag = ' <span class="urgency-today">【今天截止】</span>'
    elif urgency == 'tomorrow':
        urgency_tag = ' <span class="urgency-tomorrow">【明天截止】</span>'
    
    # 构建标题显示
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    deadline_html = f'<div class="email-deadline">⏰ 截止时间：{escape_html(deadline)}</div>' if deadline else ''
    action_html = f'<div class="email-action">✓ 行动：{escape_html(action)}</div>' if action else ''
    
    # 带DDL的学业邮件提供中英对照
    detail_html = ''
    if email and translation:
        body_clean = escape_html(email.get('body', '')[:2000])
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
    
    return f"""<li class="email-item academic">
    <div class="email-sender">• {sender}：{urgency_tag}</div>
    {subject_display}
    <div class="email-summary">{summary}</div>
    {deadline_html}
    {action_html}
    {detail_html}
</li>
"""


def render_admin_email(item, email, translation):
    """渲染行政手续邮件 - 必须提供中英对照"""
    sender = escape_html(item.get('sender', '未知发件人'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    summary = item.get('summary', '').replace('\n', '<br>')
    deadline = item.get('deadline', '')
    action = item.get('action', '')
    location = item.get('location', '')
    materials = item.get('materials', [])
    urgency = item.get('ddl_urgency', '')
    is_english = item.get('is_english', False)
    
    urgency_tag = ''
    if urgency == 'today':
        urgency_tag = ' <span class="urgency-today">【今天截止】</span>'
    elif urgency == 'tomorrow':
        urgency_tag = ' <span class="urgency-tomorrow">【明天截止】</span>'
    
    # 构建标题显示
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    deadline_html = f'<div class="email-deadline">⏰ 截止时间：{escape_html(deadline)}</div>' if deadline else ''
    action_html = f'<div class="email-action">✓ 行动：{escape_html(action)}</div>' if action else ''
    location_html = f'<div class="email-location">📍 地点：{escape_html(location)}</div>' if location else ''
    materials_html = ''
    if materials:
        materials_list = '、'.join(materials)
        materials_html = f'<div class="email-materials">📋 所需材料：{escape_html(materials_list)}</div>'
    
    # 行政手续必须提供中英对照
    detail_html = ''
    if email:
        body_clean = escape_html(email.get('body', '')[:2000])
        if translation:
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
        else:
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
    
    return f"""<li class="email-item admin">
    <div class="email-sender">• {sender}：{urgency_tag}</div>
    {subject_display}
    <div class="email-summary">{summary}</div>
    {deadline_html}
    {location_html}
    {materials_html}
    {action_html}
    {detail_html}
</li>
"""


def render_others_email(item, email, translation):
    """渲染其他邮件 - 必须提供中英对照"""
    sender = escape_html(item.get('sender', '未知发件人'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    summary = item.get('summary', '').replace('\n', '<br>')
    deadline = item.get('deadline', '')
    action = item.get('action', '')
    urgency = item.get('ddl_urgency', '')
    is_english = item.get('is_english', False)
    
    urgency_tag = ''
    if urgency == 'today':
        urgency_tag = ' <span class="urgency-today">【今天截止】</span>'
    elif urgency == 'tomorrow':
        urgency_tag = ' <span class="urgency-tomorrow">【明天截止】</span>'
    
    # 构建标题显示
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    deadline_html = f'<div class="email-deadline">⏰ 截止时间：{escape_html(deadline)}</div>' if deadline else ''
    action_html = f'<div class="email-action">✓ 行动：{escape_html(action)}</div>' if action else ''
    
    # 其他类邮件必须提供中英对照
    detail_html = ''
    if email:
        body_clean = escape_html(email.get('body', '')[:2000])
        if translation:
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
        else:
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
    
    return f"""<li class="email-item others">
    <div class="email-sender">• {sender}：{urgency_tag}</div>
    {subject_display}
    <div class="email-summary">{summary}</div>
    {deadline_html}
    {action_html}
    {detail_html}
</li>
"""


def render_newsletter_email(item, email, translation):
    """渲染Newsletter邮件 - 英文提供翻译"""
    source = escape_html(item.get('source', '未知来源'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    summary = item.get('summary', '').replace('\n', '<br>')
    is_english = item.get('is_english', False)
    
    # 构建标题显示
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    # 如果有翻译，显示展开按钮
    detail_html = ''
    if email and translation:
        body_clean = escape_html(email.get('body', '')[:2000])
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
    elif email:
        body_clean = escape_html(email.get('body', '')[:2000])
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
    
    return f"""<li class="email-item ref">
    <div class="email-sender">• {source}：</div>
    {subject_display}
    <div class="email-summary">{summary}</div>
    {detail_html}
</li>
"""


def render_subscription_email(item, email, translation):
    """渲染订阅续期邮件 - 英文提供翻译"""
    provider = escape_html(item.get('provider', '未知服务商'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    service = item.get('service', '')
    expiry = item.get('expiry', '')
    amount = item.get('amount', '')
    link = item.get('link', '')
    is_english = item.get('is_english', False)
    
    # 构建标题显示
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    details = []
    if service:
        details.append(service)
    if expiry:
        details.append(f"到期：{expiry}")
    if amount:
        details.append(f"金额：{amount}")
    if link:
        details.append(f"<a href='{escape_html(link)}' style='color:#667eea;'>操作链接</a>")
    
    detail_text = ' | '.join(details)
    
    # 如果有翻译，显示展开按钮
    detail_html = ''
    if email and translation:
        body_clean = escape_html(email.get('body', '')[:2000])
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
    elif email:
        body_clean = escape_html(email.get('body', '')[:2000])
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
    
    return f"""<li class="email-item ref">
    <div class="email-sender">• {provider}：</div>
    {subject_display}
    <div class="email-summary">{detail_text}</div>
    {detail_html}
</li>
"""


def render_other_ref_email(item, email, translation):
    """渲染其他低价值邮件 - 英文提供翻译"""
    sender = escape_html(item.get('sender', '未知发件人'))
    full_subject = escape_html(item.get('full_subject', ''))
    subject_cn = escape_html(item.get('subject_cn', ''))
    summary = item.get('summary', '')
    is_english = item.get('is_english', False)
    
    # 构建标题显示
    if is_english and subject_cn:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {subject_cn}</div><div style="color:#999;font-size:11px;margin-bottom:8px;font-style:italic;">{full_subject}</div>'
    elif full_subject:
        subject_display = f'<div style="color:#666;font-size:12px;margin-bottom:8px;">📧 {full_subject}</div>'
    else:
        subject_display = ''
    
    # 如果有翻译，显示展开按钮
    detail_html = ''
    if email and translation:
        body_clean = escape_html(email.get('body', '')[:2000])
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
    elif email:
        body_clean = escape_html(email.get('body', '')[:2000])
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
    
    return f"""<li class="email-item ref">
    <div class="email-sender">• {sender}：</div>
    {subject_display}
    <div class="email-summary">{summary}</div>
    {detail_html}
</li>
"""


def escape_html(text):
    """转义 HTML 特殊字符"""
    if not text:
        return ''
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def send_email(subject, html_content):
    """发送 QQ 邮件"""
    msg = MIMEMultipart()
    msg['From'] = QQ_EMAIL
    msg['To'] = QQ_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login(QQ_EMAIL, QQ_AUTH_CODE)
        server.send_message(msg)
    print(f"✅ 摘要已发送至 {QQ_EMAIL}")

def main():
    import sys
    # 支持命令行参数：python final_email_assistant.py 30
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print("="*60)
    print("📧 邮件助手启动 (DeepSeek AI 版)")
    print("="*60)
    print("💡 支持：翻译 + 中文摘要 + 任务识别")
    
    # 获取邮件
    print("\n📥 从 QQ 邮箱获取邮件...")
    emails = get_today_emails()
    
    if not emails:
        print("\n📭 今天没有需要处理的邮件")
        return
    
    # AI 分析
    print("\n🧠 使用 DeepSeek AI 分析...")
    analysis = analyze_with_deepseek(emails)
    
    # 统计各类邮件数量
    work_count = len(analysis.get('work', []))
    recruitment_count = len(analysis.get('recruitment', []))
    academic_count = len(analysis.get('academic', []))
    admin_count = len(analysis.get('admin', []))
    events_count = len(analysis.get('events', []))
    total_action = work_count + recruitment_count + academic_count + admin_count + events_count
    
    # 生成并发送
    print("\n📤 生成并发送摘要...")
    html = generate_html(emails, analysis)
    today = datetime.now().strftime("%m月%d日")
    send_email(f"📧 邮件日报 ({today}) - 🔴{total_action} 需处理", html)
    
    print("\n✅ 完成！请检查 QQ 邮箱收件箱")
    print(f"📊 本次分析消耗约 {total_action * 0.02:.2f} 元")

if __name__ == "__main__":
    main()
