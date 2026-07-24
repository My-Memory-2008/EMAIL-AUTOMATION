


# import imaplib
# import email
# from email.header import decode_header
# import email.utils  # Make sure this is imported at the top of your script
# import os
# import urllib.parse
# import base64
# import io
# import requests
# from PIL import Image, ImageDraw, ImageFont

# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# IMPORTANT_SENDERS = ["kaggle", "google", "youtube"]

# def text_to_image_bytes(sender, subject, body):
#     """Renders text data onto an image canvas in system memory."""
#     width = 800
#     height = 1000
#     image = Image.new("RGB", (width, height), color=(245, 245, 245))
#     draw = ImageDraw.Draw(image)
    
#     # Safely attempt to load system fonts, fall back to default if missing
#     try:
#         font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
#         bold_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
#     except IOError:
#         font = ImageFont.load_default()
#         bold_font = ImageFont.load_default()

#     draw.text((20, 20), f"Sender Address: {sender}", fill=(0, 0, 0), font=bold_font)
#     draw.text((20, 50), f"Subject Header: {subject}", fill=(0, 0, 0), font=bold_font)
#     draw.line([(20, 85), (780, 85)], fill=(180, 180, 180), width=2)
    
#     margin = 20
#     offset = 110
#     lines = []
    
#     clean_body = body[:2000].replace('\r', '')
#     for line in clean_body.split('\n'):
#         if len(line) > 80:
#             for i in range(0, len(line), 80):
#                 lines.append(line[i:i+80])
#         else:
#             lines.append(line)

#     for line in lines[:40]:
#         draw.text((margin, offset), line, fill=(50, 50, 50), font=font)
#         offset += 22

#     img_byte_arr = io.BytesIO()
#     image.save(img_byte_arr, format='JPEG')
#     return img_byte_arr.getvalue()

# def analyze_image_with_qwen(image_bytes):
#     """Feeds base64 image data directly into the local vision pipeline."""
#     base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
#     system_instruction = (
#         "You are an expert vision-capable personal secretary. Read the text printed within the input image carefully. "
#         "Categorize the document into exactly ONE of these options:\n"
#         "- Important Meeting / Event\n"
#         "- Competition Winner / Prize Notification\n"
#         "- Account Suspension / Channel Ban Risk\n"
#         "- Core Software / Platform Update\n"
#         "- Third-Party / Marketing / Low Priority\n\n"
#         "Format your output exactly like this:\n"
#         "Sender Type: [Brand / Third-Party]\n"
#         "Category: [Selected Option]\n"
#         "Summary: [1 sentence summarizing core content]\n"
#         "Action Required: [Yes/No]"
#     )

#     try:
#         response = requests.post(
#             "http://localhost:11434/api/generate",
#             json={
#                 "model": "qwen2.5vl:3b",
#                 "system": system_instruction,
#                 "prompt": "Analyze the attached email image render and extract its structural secretary brief.",
#                 "images": [base64_image],
#                 "stream": False,
#                 "options": {
#                     "temperature": 0.1
#                 }
#             },
#             timeout=240
#         )
#         if response.status_code == 200:
#             return response.json().get("response", "AI analysis processing failed.")
#     except Exception as e:
#         return f"AI Secretary Error: {str(e)}"
#     return "AI Executive Briefing Offline."

# def get_email_body(msg):
#     """Recursively walks email structure to find and extract plain text."""
#     if msg.is_multipart():
#         for part in msg.walk():
#             content_type = part.get_content_type()
#             content_disposition = str(part.get("Content-Disposition"))
            
#             # Look specifically for plain text and ignore binary attachments
#             if content_type == "text/plain" and "attachment" not in content_disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     return payload.decode(errors="ignore").strip()
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             return payload.decode(errors="ignore").strip()
            
#     return ""

# def check_email():
#     """Main scanning connection engine."""
#     # FIXED: Replaced invalid "://gmail.com" with correct IMAP server hostname
#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(EMAIL_USER, EMAIL_PASS)
#     mail.select("inbox")

#     status, messages = mail.search(None, "UNSEEN")
#     if status != "OK" or not messages or messages[0] == b'':
#         print("No new unread emails found.")
#         mail.logout()
#         return

#     email_ids = messages[0].split()
#     emails_to_process = email_ids[-1:] 

#     # for e_id in emails_to_process:
#     #     status, msg_data = mail.fetch(e_id, "(RFC822)")
#     #     for response_part in msg_data:
#     #         if isinstance(response_part, tuple):
#     #             msg = email.message_from_bytes(response_part[1])
#     #             from_header = msg.get("From", "")
#     #             print(f"📩 Checking unread email from: {from_header}") # Add this trace log
                
#     #             if any(brand in from_header.lower() for brand in IMPORTANT_SENDERS):
#     #                 # ... your existing processing logic ...
#     #                 print("🎯 Matched an important sender!")
#     #             else:
#     #                 print("⏩ Skipped: Sender not in important list.") # Add this trace log

    
#     for e_id in emails_to_process:
#         status, msg_data = mail.fetch(e_id, "(RFC822)")
#         for response_part in msg_data:
#             if isinstance(response_part, tuple):
#                 msg = email.message_from_bytes(response_part[1])
#                 from_header = msg.get("From", "")
                
#                 # Extract and parse the Date header safely
#                 raw_date = msg.get("Date", "")
#                 parsed_date = email.utils.parsedate_to_datetime(raw_date)
#                 # Format it neatly (Example: 24-Jul-2026 14:36)
#                 formatted_time = parsed_date.strftime("%d-%b-%Y %H:%M") if raw_date else "Unknown Date/Time"
                
#                 print(f"📩 [{formatted_time}] Checking unread email from: {from_header}")
                
#                 if any(brand in from_header.lower() for brand in IMPORTANT_SENDERS):
#                     print(f"🎯 Matched an important sender!")
#                     # ... rest of your processing logic ...
#                 else:
#                     print(f"⏩ Skipped: Sender not in important list.")

#     for e_id in emails_to_process:
#         status, msg_data = mail.fetch(e_id, "(RFC822)")
#         for response_part in msg_data:
#             if isinstance(response_part, tuple):
#                 msg = email.message_from_bytes(response_part[1])
#                 from_header = msg.get("From", "")
                
#                 if any(brand in from_header.lower() for brand in IMPORTANT_SENDERS):
#                     subject, encoding = decode_header(msg.get("Subject", "No Subject"))
#                     if isinstance(subject, bytes):
#                         subject = subject.decode(encoding or "utf-8")
                    
#                     # FIXED: Utilizing the updated multi-part handling function
#                     body_text = get_email_body(msg)
                    
#                     if not body_text:
#                         print("⚠️ Skipping processing: No readable text body found.")
#                         continue
                    
#                     print("🖼️ Transforming text fields into secure image matrix canvas...")
#                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
#                     print("🧠 Passing image matrix directly to Qwen2.5-VL...")
#                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
#                     msg_id = msg.get("Message-ID", "").strip("< >")
#                     encoded_id = urllib.parse.quote(msg_id)
#                     gmail_url = f"https://google.com{encoded_id}" if msg_id else "https://google.com"
                    
#                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
#                     send_ntfy_alert(ai_analysis, gmail_url, priority)
                        
#     mail.logout()

# def send_ntfy_alert(ai_analysis, email_url, priority):
#     url = f"https://ntfy.sh{NTFY_TOPIC.strip('/')}"
#     headers = {
#         "Title": "👁️ Qwen Vision Secretary Brief",
#         "Priority": priority,
#         "Tags": "camera,robot",
#         "Click": email_url
#     }
#     data = f"{ai_analysis}\n\n👉 Tap this notification to open email."
#     requests.post(url, data=data.encode('utf-8'), headers=headers)

# if __name__ == "__main__":
#     check_email()




import imaplib
import email
from email.header import decode_header
import email.utils
import os
import urllib.parse
import base64
import io
import requests
from datetime import datetime
import pytz  # Handles accurate timezone dates
from PIL import Image, ImageDraw, ImageFont

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# Target folders to capture every single section of Gmail
GMAIL_FOLDERS = ["[Gmail]/All Mail", "[Gmail]/Spam"]

def text_to_image_bytes(sender, subject, body):
    """Renders text data onto an image canvas in system memory."""
    width = 800
    height = 1000
    image = Image.new("RGB", (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        bold_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except IOError:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()

    draw.text((20, 20), f"Sender Address: {sender}", fill=(0, 0, 0), font=bold_font)
    draw.text((20, 50), f"Subject Header: {subject}", fill=(0, 0, 0), font=bold_font)
    draw.line([(20, 85), (780, 85)], fill=(180, 180, 180), width=2)
    
    margin = 20
    offset = 110
    lines = []
    
    clean_body = body[:2000].replace('\r', '')
    for line in clean_body.split('\n'):
        if len(line) > 80:
            for i in range(0, len(line), 80):
                lines.append(line[i:i+80])
        else:
            lines.append(line)

    for line in lines[:40]:
        draw.text((margin, offset), line, fill=(50, 50, 50), font=font)
        offset += 22

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def analyze_image_with_qwen(image_bytes):
    """Feeds base64 image data directly into the local vision pipeline."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    system_instruction = (
        "You are an expert vision-capable personal secretary. Read the text printed within the input image carefully. "
        "Categorize the document into exactly ONE of these options:\n"
        "- Important Meeting / Event\n"
        "- Competition Winner / Prize Notification\n"
        "- Account Suspension / Channel Ban Risk\n"
        "- Core Software / Platform Update\n"
        "- Third-Party / Marketing / Low Priority\n\n"
        "Format your output exactly like this:\n"
        "Sender Type: [Brand / Third-Party]\n"
        "Category: [Selected Option]\n"
        "Summary: [1 sentence summarizing core content]\n"
        "Action Required: [Yes/No]"
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5vl:3b",
                "system": system_instruction,
                "prompt": "Analyze the attached email image render and extract its structural secretary brief.",
                "images": [base64_image],
                "stream": False,
                "options": { "temperature": 0.1 }
            },
            timeout=240
        )
        if response.status_code == 200:
            return response.json().get("response", "AI analysis processing failed.")
    except Exception as e:
        return f"AI Secretary Error: {str(e)}"
    return "AI Executive Briefing Offline."

def get_email_body(msg):
    """Recursively walks email structure to find and extract plain text or HTML fallback."""
    html_body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore").strip()
            elif content_type == "text/html" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    html_body = payload.decode(errors="ignore").strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore").strip()
            
    # If no plain text exists, fall back to raw HTML string content
    return html_body if html_body else "No readable text content found."


def check_email():
    """Main scanning connection engine with automatic folder name detection."""
    mail = imaplib.IMAP4_SSL("://gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)

    user_tz = pytz.timezone("Asia/Kolkata") 
    today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
    print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

    # 1. Dynamically discover real folder paths to prevent localization errors
    status, folder_list = mail.list()
    all_mail_folder = None
    spam_folder = None

    if status == "OK":
        for folder_info in folder_list:
            folder_string = folder_info.decode("utf-8", errors="ignore")
            # Gmail flags All Mail as \All and Spam as \Spam internally
            if r"\All" in folder_string:
                all_mail_folder = folder_string.split(' "/" ')[-1].strip('"')
            elif r"\Spam" in folder_string:
                spam_folder = folder_string.split(' "/" ')[-1].strip('"')

    # Fallback to defaults if auto-detection fails
    target_folders = []
    if all_mail_folder: target_folders.append(all_mail_folder)
    else: target_folders.append("[Gmail]/All Mail")
    
    if spam_folder: target_folders.append(spam_folder)
    else: target_folders.append("[Gmail]/Spam")

    processed_message_ids = set()

    # 2. Begin scanning the discovered folders
    for folder in target_folders:
        print(f"📂 Opening Folder Location: {folder}...")
        try:
            status, _ = mail.select(folder, readonly=True)
            if status != "OK":
                print(f"⚠️ Could not open folder {folder}. Skipping...")
                continue
            
            # Use separate tokens to guarantee strict syntax safety
            status, messages = mail.search(None, 'SINCE', today_imap_str)
            if status != "OK" or not messages or messages[0] == b'':
                print(f"🏖️ No emails found in {folder} from today.")
                continue

            email_ids = messages[0].split()
            print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.")

            for e_id in email_ids:
                status, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        msg_id = msg.get("Message-ID", "").strip("< >")
                        if not msg_id or msg_id in processed_message_ids:
                            continue
                        processed_message_ids.add(msg_id)

                        from_header = msg.get("From", "")
                        raw_date = msg.get("Date", "")
                        
                        try:
                            parsed_date = email.utils.parsedate_to_datetime(raw_date)
                            formatted_time = parsed_date.strftime("%H:%M:%S")
                        except Exception:
                            formatted_time = "Unknown Time"

                        subject, encoding = decode_header(msg.get("Subject", "No Subject"))
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8", errors="ignore")

                        print(f"📥 [{formatted_time}] Processing: From: {from_header} | Subject: {subject}")
                        
                        body_text = get_email_body(msg)
                        
                        print("🖼️ Transforming text fields into secure image matrix canvas...")
                        img_bytes = text_to_image_bytes(from_header, subject, body_text)
                        
                        print("🧠 Passing image matrix directly to Qwen2.5-VL...")
                        ai_analysis = analyze_image_with_qwen(img_bytes)
                        
                        encoded_id = urllib.parse.quote(msg_id)
                        gmail_url = f"https://google.com{encoded_id}"
                        
                        priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                        
                        send_ntfy_alert(ai_analysis, gmail_url, priority)
                        print("✅ Analysis dispatched via ntfy successfully.\n")
                        
        except Exception as folder_error:
            print(f"❌ Error while scanning folder {folder}: {str(folder_error)}")

    mail.logout()

def send_ntfy_alert(ai_analysis, email_url, priority):
    url = f"https://ntfy.sh{NTFY_TOPIC.strip('/')}"
    headers = {
        "Title": "👁️ Qwen Vision Secretary Brief",
        "Priority": priority,
        "Tags": "camera,robot",
        "Click": email_url
    }
    data = f"{ai_analysis}\n\n👉 Tap this notification to open email."
    requests.post(url, data=data.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    check_email()
