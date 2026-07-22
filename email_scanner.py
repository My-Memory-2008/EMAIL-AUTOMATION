import imaplib
import email
from email.header import decode_header
import os
import urllib.parse
import base64
import io
import requests
from PIL import Image, ImageDraw, ImageFont

# Initialize environments
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# Targeting parameters 
IMPORTANT_SENDERS = ["kaggle", "google", "youtube"]

def text_to_image_bytes(sender, subject, body):
    """Encodes private text safely directly into a raw image binary matrix."""
    width = 800
    height = 1000
    image = Image.new("RGB", (width, height), color=(242, 242, 242))
    draw = ImageDraw.Draw(image)
    
    # Try loading clean TrueType system assets, fallback to standard terminal bitmapping if missing
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        bold_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    except IOError:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()

    # Draw masked tracking indicators
    draw.text((25, 25), f"Origin Vector: {sender}", fill=(10, 10, 10), font=bold_font)
    draw.text((25, 55), f"Topic Header: {subject}", fill=(10, 10, 10), font=bold_font)
    draw.line([(25, 90), (775, 90)], fill=(190, 190, 190), width=2)
    
    margin = 25
    offset = 115
    lines = []
    
    # Standardize and partition formatting array fields
    clean_body = body[:2000].replace('\r', '')
    for line in clean_body.split('\n'):
        if len(line) > 85:
            for i in range(0, len(line), 85):
                lines.append(line[i:i+85])
        else:
            lines.append(line)

    for line in lines[:38]:
        draw.text((margin, offset), line, fill=(40, 40, 40), font=font)
        offset += 22

    # Save directly to virtual memory stream array
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def analyze_image_with_qwen(image_bytes):
    """Streams data arrays directly to local neural layers."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    system_instruction = (
        "You are an expert vision personal secretary. Read the text inside the image matrix.\n"
        "Categorize the content into exactly ONE option:\n"
        "- Important Meeting / Event\n"
        "- Competition Winner / Prize Notification\n"
        "- Account Suspension / Channel Ban Risk\n"
        "- Core Software / Platform Update\n"
        "- Third-Party / Marketing / Low Priority\n\n"
        "Provide your response precisely in this template layout:\n"
        "Sender Type: [Brand / Third-Party]\n"
        "Category: [Selected Option]\n"
        "Summary: [1 sentence summarizing content insights]\n"
        "Action Required: [Yes/No]"
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5vl:3b",
                "system": system_instruction,
                "prompt": "Extract the structured personal secretary briefing from the email visualization canvas.",
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 120
                }
            },
            timeout=240
        )
        if response.status_code == 200:
            return response.json().get("response", "AI processing anomaly.")
    except Exception as e:
        return f"AI Script Execution Log Error: {str(e)}"
    return "Local Processing Engine Timeout."

def get_email_body(msg):
    """Pulls clean, unformatted text parts."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")
    return body.strip()


def check_email():
    """Establishes Gmail IMAP handshake and parses parameters cleanly."""
    mail = imaplib.IMAP4_SSL("://gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")
    if status != "OK" or not messages or messages[0] == b'':
        print("Inbox clean. No new unseen messages flagged.")
        return

    # FIXED: Unpacks the first element of the list before executing split
    email_ids = messages[0].split()
    
    # Process only the single most recent mail to protect workflow timeout caps
    emails_to_process = email_ids[-1:] 

    for e_id in emails_to_process:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part)
                from_header = msg.get("From", "")
                
                # Check for sender brand validation matches
                if any(brand in from_header.lower() for brand in IMPORTANT_SENDERS):
                    subject, encoding = decode_header(msg.get("Subject", "No Subject"))
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    
                    body_text = get_email_body(msg)
                    
                    print("🔄 Processing target match. Compiling matrix array canvas...")
                    img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
                    print("🧠 Forwarding vector maps into local model layers...")
                    ai_analysis = analyze_image_with_qwen(img_bytes)
                    
                    # Generate deep-linking reference indicators
                    msg_id = msg.get("Message-ID", "").strip("< >")
                    encoded_id = urllib.parse.quote(msg_id)
                    gmail_url = f"https://google.com:{encoded_id}" if msg_id else "https://google.com"
                    
                    priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
                    send_ntfy_alert(ai_analysis, gmail_url, priority)
                        
    mail.logout()


def send_ntfy_alert(ai_analysis, email_url, priority):
    """Dispatches structural secretary summaries to the mobile listener endpoint."""
    url = f"https://ntfy.sh{NTFY_TOPIC}"
    headers = {
        "Title": "👁️ Qwen Vision Secretary Report",
        "Priority": priority,
        "Tags": "camera,robot",
        "Click": email_url
    }
    data = f"{ai_analysis}\n\n👉 Tap notification to immediately inspect source mail thread."
    requests.post(url, data=data, headers=headers)

if __name__ == "__main__":
    check_email()
