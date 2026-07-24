


import imaplib
import email
from email.header import decode_header
import email.utils  # Make sure this is imported at the top of your script
import os
import urllib.parse
import base64
import io
import requests
from PIL import Image, ImageDraw, ImageFont

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

IMPORTANT_SENDERS = ["kaggle", "google", "youtube"]

def text_to_image_bytes(sender, subject, body):
    """Renders text data onto an image canvas in system memory."""
    width = 800
    height = 1000
    image = Image.new("RGB", (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(image)
    
    # Safely attempt to load system fonts, fall back to default if missing
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
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=240
        )
        if response.status_code == 200:
            return response.json().get("response", "AI analysis processing failed.")
    except Exception as e:
        return f"AI Secretary Error: {str(e)}"
    return "AI Executive Briefing Offline."

def get_email_body(msg):
    """Recursively walks email structure to find and extract plain text."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Look specifically for plain text and ignore binary attachments
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore").strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore").strip()
            
    return ""

def check_email():
    """Main scanning connection engine."""
    # FIXED: Replaced invalid "://gmail.com" with correct IMAP server hostname
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")
    if status != "OK" or not messages or messages[0] == b'':
        print("No new unread emails found.")
        mail.logout()
        return

    email_ids = messages[0].split()
    emails_to_process = email_ids[-1:] 
    for e_id in emails_to_process:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                from_header = msg.get("From", "")
                print(f"📩 Checking unread email from: {from_header}") # Add this trace log
                
                if any(brand in from_header.lower() for brand in IMPORTANT_SENDERS):
                    # ... your existing processing logic ...
                    print("🎯 Matched an important sender!")
                else:
                    print("⏩ Skipped: Sender not in important list.") # Add this trace log

    for e_id in emails_to_process:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                from_header = msg.get("From", "")
                
                if any(brand in from_header.lower() for brand in IMPORTANT_SENDERS):
                    subject, encoding = decode_header(msg.get("Subject", "No Subject"))
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    
                    # FIXED: Utilizing the updated multi-part handling function
                    body_text = get_email_body(msg)
                    
                    if not body_text:
                        print("⚠️ Skipping processing: No readable text body found.")
                        continue
                    
                    print("🖼️ Transforming text fields into secure image matrix canvas...")
                    img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
                    print("🧠 Passing image matrix directly to Qwen2.5-VL...")
                    ai_analysis = analyze_image_with_qwen(img_bytes)
                    
                    msg_id = msg.get("Message-ID", "").strip("< >")
                    encoded_id = urllib.parse.quote(msg_id)
                    gmail_url = f"https://google.com{encoded_id}" if msg_id else "https://google.com"
                    
                    priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
                    send_ntfy_alert(ai_analysis, gmail_url, priority)
                        
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
