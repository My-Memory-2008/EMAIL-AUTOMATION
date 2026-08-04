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




# import imaplib
# import email
# from email.header import decode_header
# import email.utils
# import os
# import urllib.parse
# import base64
# import io
# import requests
# from datetime import datetime
# import pytz
# from PIL import Image, ImageDraw, ImageFont

# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# MEMORY_FILE = "processed_emails.txt"

# def load_ai_memory():
#     """Loads handled email tracking strings from the local file storage."""
#     if not os.path.exists(MEMORY_FILE):
#         return set()
#     with open(MEMORY_FILE, "r", encoding="utf-8") as f:
#         return set(line.strip() for line in f if line.strip())

# def save_to_ai_memory(msg_id):
#     """Saves a processed message hash permanently onto the local file."""
#     with open(MEMORY_FILE, "a", encoding="utf-8") as f:
#         f.write(f"{msg_id}\n")

# def text_to_image_bytes(sender, subject, body):
#     """Renders text data onto an image canvas in system memory."""
#     width = 800
#     height = 1000
#     image = Image.new("RGB", (width, height), color=(245, 245, 245))
#     draw = ImageDraw.Draw(image)
    
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
#                 "options": { "temperature": 0.1 }
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
#     """Main scanning connection engine exploring all folders sequentially."""
#     try:
#         print("🔐 Connecting to Gmail IMAP server...")
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         print("✅ Successfully connected to Gmail!")
#     except Exception as conn_error:
#         print(f"❌ IMAP Connection Failed: {str(conn_error)}")
#         print("⚠️ Verify EMAIL_USER and EMAIL_PASS environment variables are set correctly.")
#         return
    
#     try:
#         mail.login(EMAIL_USER, EMAIL_PASS)
#         print("✅ Successfully logged in!")
#     except Exception as login_error:
#         print(f"❌ Login Failed: {str(login_error)}")
#         print("⚠️ Check your email credentials.")
#         mail.logout()
#         return

#     user_tz = pytz.timezone("Asia/Kolkata") 
#     today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
#     print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

#     ai_read_memory = load_ai_memory()
#     target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
#     processed_count = 0

#     for folder in target_folders:
#         try:
#             print(f"📂 Opening Folder Location: {folder}...")
#             status, _ = mail.select(f'"{folder}"', readonly=True)
#             if status != "OK":
#                 print(f"⚠️ Could not select folder: {folder}")
#                 continue
            
#             status, messages = mail.search(None, 'SINCE', today_imap_str)
#             if status != "OK" or not messages:
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             # Extract IMAP list arrays cleanly without crashing
#             raw_bytes = messages[0] if isinstance(messages, list) else messages
#             if not raw_bytes or raw_bytes == b'':
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             email_ids = raw_bytes.split()
#             print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

#             # Process each individual email one by one safely
#             for e_id in email_ids:
#                 try:
#                     status, msg_data = mail.fetch(e_id, "(RFC822)")
#                     if status != "OK":
#                         print(f"⚠️ Could not fetch email ID {e_id.decode()}")
#                         continue
                    
#                     # FIXED: Handle the IMAP response structure correctly
#                     msg_content = None
#                     if msg_data and isinstance(msg_data, list):
#                         for response_part in msg_data:
#                             # response_part can be a tuple (headers, body) or just bytes
#                             if isinstance(response_part, tuple):
#                                 msg_content = response_part[1]
#                                 break
#                             elif isinstance(response_part, bytes):
#                                 msg_content = response_part
#                                 break
                    
#                     if msg_content is None:
#                         print(f"⚠️ No valid message content found for email ID {e_id.decode()}")
#                         continue
                    
#                     # Parse the email message
#                     try:
#                         msg = email.message_from_bytes(msg_content)
#                     except Exception as parse_error:
#                         print(f"⚠️ Error parsing email ID {e_id.decode()}: {str(parse_error)}")
#                         continue
                    
#                     msg_id = msg.get("Message-ID", "")
#                     if msg_id:
#                         msg_id = msg_id.strip("< >")
#                     else:
#                         msg_id = f"generated-id-{e_id.decode()}"
                    
#                     # AI Memory Evaluation Check
#                     if msg_id in ai_read_memory:
#                         print(f"⏩ Skipping: Email ID {msg_id} already marked as read in AI Memory.")
#                         continue

#                     from_header = msg.get("From", "Unknown Sender")
#                     raw_date = msg.get("Date", "")
                    
#                     try:
#                         parsed_date = email.utils.parsedate_to_datetime(raw_date)
#                         formatted_time = parsed_date.strftime("%H:%M:%S")
#                     except Exception:
#                         formatted_time = "Unknown Time"

#                     subject, encoding = decode_header(msg.get("Subject", "No Subject"))
#                     if isinstance(subject, bytes):
#                         subject = subject.decode(encoding or "utf-8", errors="ignore")

#                     print(f"📥 [{formatted_time}] Processing Single Mail:")
#                     print(f"   From: {from_header}")
#                     print(f"   Subject: {subject}")
                    
#                     body_text = get_email_body(msg)
#                     if not body_text:
#                         print("⚠️ Skipping processing: No readable text body found.\n")
#                         continue

#                     print("🖼️ Transforming text fields into secure image matrix canvas...")
#                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
#                     print("🧠 Passing image matrix directly to Qwen2.5-VL...")
#                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
#                     print(f"\n🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
#                     # Process notification actions using baseline parameters
#                     encoded_id = urllib.parse.quote(msg_id)
#                     gmail_url = f"https://google.com{encoded_id}"
#                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
#                     send_ntfy_alert(ai_analysis, gmail_url, priority)
#                     print("✅ Analysis dispatched via ntfy successfully.")
                    
#                     # Mark item as read inside AI memory without changing Gmail state
#                     save_to_ai_memory(msg_id)
#                     ai_read_memory.add(msg_id)
#                     processed_count += 1
#                     print(f"💾 Marked as Read in AI Memory: {msg_id}\n")
#                     print("=" * 80 + "\n")
                    
#                 except Exception as single_mail_error:
#                     print(f"⚠️ Error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
#                     import traceback
#                     traceback.print_exc()
#                     continue
        
#         except Exception as folder_error:
#             print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
#             import traceback
#             traceback.print_exc()
#             continue

#     mail.logout()
#     print("=" * 80)
#     print(f"✅ IMAP connection closed.")
#     print(f"📊 Processed {processed_count} email(s) in this run.")
#     print(f"📂 Total processed emails in memory: {len(ai_read_memory)}")

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





# import imaplib
# import email
# from email.header import decode_header
# import email.utils
# import os
# import urllib.parse
# import base64
# import io
# import requests
# from datetime import datetime
# import pytz
# from PIL import Image, ImageDraw, ImageFont

# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# MEMORY_FILE = "processed_emails.txt"

# def load_ai_memory():
#     """Loads handled email tracking strings from the local file storage."""
#     if not os.path.exists(MEMORY_FILE):
#         return set()
#     with open(MEMORY_FILE, "r", encoding="utf-8") as f:
#         return set(line.strip() for line in f if line.strip())

# def save_to_ai_memory(msg_id):
#     """Saves a processed message hash permanently onto the local file."""
#     with open(MEMORY_FILE, "a", encoding="utf-8") as f:
#         f.write(f"{msg_id}\n")

# def text_to_image_bytes(sender, subject, body):
#     """Renders text data onto an image canvas in system memory."""
#     width = 800
#     height = 1000
#     image = Image.new("RGB", (width, height), color=(245, 245, 245))
#     draw = ImageDraw.Draw(image)
    
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
#                 "options": { "temperature": 0.1 }
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
            
#             if content_type == "text/plain" and "attachment" not in content_disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     return payload.decode(errors="ignore").strip()
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             return payload.decode(errors="ignore").strip()
            
#     return ""




# # def check_email():
# #     """Main scanning connection engine exploring all folders sequentially."""
# #     try:
# #         print("🔐 Connecting to Gmail IMAP server...")
# #         mail = imaplib.IMAP4_SSL("imap.gmail.com")
# #         print("✅ Successfully connected to Gmail!")
# #     except Exception as conn_error:
# #         print(f"❌ IMAP Connection Failed: {str(conn_error)}")
# #         return
    
# #     try:
# #         mail.login(EMAIL_USER, EMAIL_PASS)
# #         print("✅ Successfully logged in!")
# #     except Exception as login_error:
# #         print(f"❌ Login Failed: {str(login_error)}")
# #         mail.logout()
# #         return

# #     user_tz = pytz.timezone("Asia/Kolkata") 
# #     today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
# #     print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

# #     ai_read_memory = load_ai_memory()
# #     target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
# #     processed_count = 0

# #     for folder in target_folders:
# #         try:
# #             print(f"📂 Opening Folder Location: {folder}...")
# #             status, _ = mail.select(f'"{folder}"', readonly=True)
# #             if status != "OK":
# #                 print(f"⚠️ Could not select folder: {folder}")
# #                 continue
            
# #             status, messages = mail.search(None, 'SINCE', today_imap_str)
# #             if status != "OK" or not messages:
# #                 print(f"🏖️ No emails found in {folder} from today.")
# #                 continue

# #             raw_bytes = messages[0] if isinstance(messages, list) else messages
# #             if not raw_bytes or raw_bytes == b'':
# #                 print(f"🏖️ No emails found in {folder} from today.")
# #                 continue

# #             email_ids = raw_bytes.split()
# #             print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

# #             for e_id in email_ids:
# #                 try:
# #                     status, msg_data = mail.fetch(e_id, "(RFC822)")
# #                     if status != "OK":
# #                         continue
                    
# #                     msg_content = None
# #                     if msg_data and isinstance(msg_data, list):
# #                         for response_part in msg_data:
# #                             if isinstance(response_part, tuple):
# #                                 msg_content = response_part[1]
# #                                 break
# #                             elif isinstance(response_part, bytes):
# #                                 msg_content = response_part
# #                                 break
                    
# #                     if msg_content is None:
# #                         continue
                    
# #                     try:
# #                         msg = email.message_from_bytes(msg_content)
# #                     except Exception:
# #                         continue
                    
# #                     msg_id = msg.get("Message-ID", "")
# #                     if msg_id:
# #                         msg_id = msg_id.strip("< >")
# #                     else:
# #                         msg_id = f"generated-id-{e_id.decode()}"
                    
# #                     if msg_id in ai_read_memory:
# #                         continue

# #                     from_header = msg.get("From", "Unknown Sender")
# #                     raw_date = msg.get("Date", "")
                    
# #                     try:
# #                         parsed_date = email.utils.parsedate_to_datetime(raw_date)
# #                         formatted_time = parsed_date.strftime("%H:%M:%S")
# #                     except Exception:
# #                         formatted_time = "Unknown Time"

# #                     # --- FIX STARTS HERE ---
# #                     raw_subject = msg.get("Subject", "No Subject")
# #                     decoded_parts = decode_header(raw_subject)
                    
# #                     # decode_header returns a list of tuples: [(string, encoding), ...]
# #                     # We take the first part and decode it safely
# #                     if decoded_parts:
# #                         part, encoding = decoded_parts[0]
# #                         if isinstance(part, bytes):
# #                             # If it's bytes, decode using the provided encoding or utf-8
# #                             subject = part.decode(encoding or 'utf-8', errors='ignore')
# #                         else:
# #                             # If it's already a string
# #                             subject = part
# #                     else:
# #                         subject = "No Subject"
# #                     # --- FIX ENDS HERE ---

# #                     print(f"📥 [{formatted_time}] Processing Single Mail:")
# #                     print(f"   From: {from_header}")
# #                     print(f"   Subject: {subject}")
                    
# #                     body_text = get_email_body(msg)
# #                     if not body_text:
# #                         print("⚠️ Skipping processing: No readable text body found.\n")
# #                         continue

# #                     print("🖼️ Transforming text fields into secure image matrix canvas...")
# #                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
# #                     print("🧠 Passing image matrix directly to Qwen2.5-VL...")
# #                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
# #                     print(f"\n🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
# #                     encoded_id = urllib.parse.quote(msg_id)
# #                     gmail_url = f"https://google.com{encoded_id}"
# #                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
# #                     send_ntfy_alert(ai_analysis, gmail_url, priority)
# #                     print("✅ Analysis dispatched via ntfy successfully.")
                    
# #                     save_to_ai_memory(msg_id)
# #                     ai_read_memory.add(msg_id)
# #                     processed_count += 1
# #                     print(f"💾 Marked as Read in AI Memory: {msg_id}\n")
# #                     print("=" * 80 + "\n")
                    
# #                 except Exception as single_mail_error:
# #                     print(f"⚠️ Error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
# #                     import traceback
# #                     traceback.print_exc()
# #                     continue
        
# #         except Exception as folder_error:
# #             print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
# #             import traceback
# #             traceback.print_exc()
# #             continue

# #     mail.logout()
# #     print("=" * 80)
# #     print(f"✅ IMAP connection closed.")
# #     print(f"📊 Processed {processed_count} email(s) in this run.")
# #     print(f"📂 Total processed emails in memory: {len(ai_read_memory)}")





# def check_email():
#     """Main scanning connection engine exploring all folders sequentially."""
#     try:
#         print("🔐 Connecting to Gmail IMAP server...")
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         print("✅ Successfully connected to Gmail!")
#     except Exception as conn_error:
#         print(f"❌ IMAP Connection Failed: {str(conn_error)}")
#         return
    
#     try:
#         mail.login(EMAIL_USER, EMAIL_PASS)
#         print("✅ Successfully logged in!")
#     except Exception as login_error:
#         print(f"❌ Login Failed: {str(login_error)}")
#         mail.logout()
#         return

#     user_tz = pytz.timezone("Asia/Kolkata") 
#     today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
#     print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

#     ai_read_memory = load_ai_memory()
#     target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
#     processed_count = 0

#     for folder in target_folders:
#         try:
#             print(f"📂 Opening Folder Location: {folder}...")
#             status, _ = mail.select(f'"{folder}"', readonly=True)
#             if status != "OK":
#                 print(f"⚠️ Could not select folder: {folder}")
#                 continue
            
#             status, messages = mail.search(None, 'SINCE', today_imap_str)
#             if status != "OK" or not messages:
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             raw_bytes = messages[0] if isinstance(messages, list) else messages
#             if not raw_bytes or raw_bytes == b'':
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             email_ids = raw_bytes.split()
#             print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

#             for e_id in email_ids:
#                 try:
#                     status, msg_data = mail.fetch(e_id, "(RFC822)")
#                     if status != "OK":
#                         continue
                    
#                     msg_content = None
#                     if msg_data and isinstance(msg_data, list):
#                         for response_part in msg_data:
#                             if isinstance(response_part, tuple):
#                                 msg_content = response_part[1]
#                                 break
#                             elif isinstance(response_part, bytes):
#                                 msg_content = response_part
#                                 break
                    
#                     if msg_content is None:
#                         continue
                    
#                     try:
#                         msg = email.message_from_bytes(msg_content)
#                     except Exception:
#                         continue
                    
#                     msg_id = msg.get("Message-ID", "")
#                     if msg_id:
#                         msg_id = msg_id.strip("< >")
#                     else:
#                         msg_id = f"generated-id-{e_id.decode()}"
                    
#                     if msg_id in ai_read_memory:
#                         continue

#                     # ... inside the loop where you process each email ...
                    
#                     from_header = msg.get("From", "Unknown Sender")
#                     raw_date = msg.get("Date", "")
                    
#                     try:
#                         # 1. Parse the raw date string from the email header
#                         parsed_date = email.utils.parsedate_to_datetime(raw_date)
                        
#                         # 2. Convert it to Indian Standard Time (IST)
#                         ist_date = parsed_date.astimezone(user_tz)
                        
#                         # 3. Format it to show only the time (or include date if you prefer)
#                         formatted_time = ist_date.strftime("%H:%M:%S") 
                        
#                         # Optional: If you want to see the date too, use:
#                         # formatted_time = ist_date.strftime("%d-%b %H:%M")
                        
#                     except Exception:
#                         formatted_time = "Unknown Time"

#                     print(f"📥 [{formatted_time} IST] Processing Single Mail:")                    
#                     print(f"   From: {from_header}")
#                     print(f"   Subject: {subject}")
                    
#                     body_text = get_email_body(msg)
#                     if not body_text:
#                         print("⚠️ Skipping processing: No readable text body found.\n")
#                         continue

#                     print("🖼️ Transforming text fields into secure image matrix canvas...")
#                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
#                     print("🧠 Passing image matrix directly to Qwen2.5-VL...")
#                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
#                     print(f"\n🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
#                     encoded_id = urllib.parse.quote(msg_id)
#                     gmail_url = f"https://google.com{encoded_id}"
#                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
#                     send_ntfy_alert(ai_analysis, gmail_url, priority)
#                     print("✅ Analysis dispatched via ntfy successfully.")
                    
#                     save_to_ai_memory(msg_id)
#                     ai_read_memory.add(msg_id)
#                     processed_count += 1
#                     print(f"💾 Marked as Read in AI Memory: {msg_id}\n")
#                     print("=" * 80 + "\n")
                    
#                 except Exception as single_mail_error:
#                     print(f"⚠️ Error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
#                     import traceback
#                     traceback.print_exc()
#                     continue
        
#         except Exception as folder_error:
#             print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
#             import traceback
#             traceback.print_exc()
#             continue

#     mail.logout()
#     print("=" * 80)
#     print(f"✅ IMAP connection closed.")
#     print(f"📊 Processed {processed_count} email(s) in this run.")
#     print(f"📂 Total processed emails in memory: {len(ai_read_memory)}")




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



# import imaplib
# import email
# from email.header import decode_header
# import email.utils
# import os
# import urllib.parse
# import base64
# import io
# import re # Import the regular expression module
# import requests
# from datetime import datetime
# import pytz
# from PIL import Image, ImageDraw, ImageFont

# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# MEMORY_FILE = "processed_emails.txt"

# def load_ai_memory():
#     """Loads handled email tracking strings from the local file storage."""
#     if not os.path.exists(MEMORY_FILE):
#         return set()
#     with open(MEMORY_FILE, "r", encoding="utf-8") as f:
#         return set(line.strip() for line in f if line.strip())

# def save_to_ai_memory(msg_id):
#     """Saves a processed message hash permanently onto the local file."""
#     with open(MEMORY_FILE, "a", encoding="utf-8") as f:
#         f.write(f"{msg_id}\n")

# def text_to_image_bytes(sender, subject, body):
#     """Renders text data onto an image canvas in system memory."""
#     width = 800
#     height = 1000
#     image = Image.new("RGB", (width, height), color=(245, 245, 245))
#     draw = ImageDraw.Draw(image)
    
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
#                 "options": { "temperature": 0.1 }
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
            
#             if content_type == "text/plain" and "attachment" not in content_disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     return payload.decode(errors="ignore").strip()
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             return payload.decode(errors="ignore").strip()
            
#     return ""

# def extract_emails_from_text(text):
#     """
#     Extracts email addresses from a given text string using a regular expression.
#     This function finds all substrings matching the typical email pattern.
#     """
#     # Regular expression pattern for email addresses
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     # Find all matches in the provided text
#     found_emails = re.findall(email_pattern, text)
#     # Return a list of unique email addresses found
#     return list(set(found_emails)) # Using set to remove potential duplicates


# def check_email():
#     """Main scanning connection engine exploring all folders sequentially."""
#     try:
#         print("🔐 Connecting to Gmail IMAP server...")
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         print("✅ Successfully connected to Gmail!")
#     except Exception as conn_error:
#         print(f"❌ IMAP Connection Failed: {str(conn_error)}")
#         return
    
#     try:
#         mail.login(EMAIL_USER, EMAIL_PASS)
#         print("✅ Successfully logged in!")
#     except Exception as login_error:
#         print(f"❌ Login Failed: {str(login_error)}")
#         mail.logout()
#         return

#     user_tz = pytz.timezone("Asia/Kolkata") 
#     today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
#     print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

#     ai_read_memory = load_ai_memory()
#     target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
#     processed_count = 0

#     for folder in target_folders:
#         try:
#             print(f"📂 Opening Folder Location: {folder}...")
#             status, _ = mail.select(f'"{folder}"', readonly=True)
#             if status != "OK":
#                 print(f"⚠️ Could not select folder: {folder}")
#                 continue
            
#             status, messages = mail.search(None, 'SINCE', today_imap_str)
#             if status != "OK" or not messages:
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             raw_bytes = messages[0] if isinstance(messages, list) else messages
#             if not raw_bytes or raw_bytes == b'':
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             email_ids = raw_bytes.split()
#             print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

#             for e_id in email_ids:
#                 try:
#                     status, msg_data = mail.fetch(e_id, "(RFC822)")
#                     if status != "OK":
#                         continue
                    
#                     msg_content = None
#                     if msg_data and isinstance(msg_data, list):
#                         for response_part in msg_data:
#                             if isinstance(response_part, tuple):
#                                 msg_content = response_part[1]
#                                 break
#                             elif isinstance(response_part, bytes):
#                                 msg_content = response_part
#                                 break
                    
#                     if msg_content is None:
#                         continue
                    
#                     try:
#                         msg = email.message_from_bytes(msg_content)
#                     except Exception:
#                         continue
                    
#                     msg_id = msg.get("Message-ID", "")
#                     if msg_id:
#                         msg_id = msg_id.strip("< >")
#                     else:
#                         msg_id = f"generated-id-{e_id.decode()}"
                    
#                     if msg_id in ai_read_memory:
#                         continue

#                     from_header = msg.get("From", "Unknown Sender")
#                     raw_date = msg.get("Date", "")
                    
#                     try:
#                         # 1. Parse the raw date string from the email header
#                         parsed_date = email.utils.parsedate_to_datetime(raw_date)
                        
#                         # 2. Convert it to Indian Standard Time (IST)
#                         ist_date = parsed_date.astimezone(user_tz)
                        
#                         # 3. Format it to show only the time (or include date if you prefer)
#                         formatted_time = ist_date.strftime("%H:%M:%S") 
                        
#                         # Optional: If you want to see the date too, use:
#                         # formatted_time = ist_date.strftime("%d-%b %H:%M")
                        
#                     except Exception:
#                         formatted_time = "Unknown Time"

#                     # --- FIX FOR SUBJECT DECODING ---
#                     raw_subject = msg.get("Subject", "No Subject")
#                     decoded_parts = decode_header(raw_subject)
                    
#                     if decoded_parts:
#                         part, encoding = decoded_parts[0]
#                         if isinstance(part, bytes):
#                             subject = part.decode(encoding or 'utf-8', errors='ignore')
#                         else:
#                             subject = part
#                     else:
#                         subject = "No Subject"
#                     # --- END FIX ---

#                     print(f"📥 [{formatted_time} IST] Processing Single Mail:")                    
#                     print(f"   From: {from_header}")
#                     print(f"   Subject: {subject}")
                    
#                     body_text = get_email_body(msg)
#                     if not body_text:
#                         print("⚠️ Skipping processing: No readable text body found.\n")
#                         continue

#                     # --- EXTRACT EMAILS FROM THE BODY ---
#                     extracted_emails = extract_emails_from_text(body_text)
#                     print(f"   Emails found in body: {extracted_emails}") # Print the found emails

#                     print("🖼️ Transforming text fields into secure image matrix canvas...")
#                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
#                     print("🧠 Passing image matrix directly to Qwen2.5-VL...")
#                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
#                     print(f"\n🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
#                     encoded_id = urllib.parse.quote(msg_id)
#                     gmail_url = f"https://google.com{encoded_id}"
#                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
#                     # Include extracted emails in the alert if any were found
#                     alert_body = ai_analysis
#                     if extracted_emails:
#                          alert_body += f"\n\n📧 Emails found in body: {', '.join(extracted_emails)}"

#                     send_ntfy_alert(alert_body, gmail_url, priority) # Send the modified alert
#                     print("✅ Analysis dispatched via ntfy successfully.")
                    
#                     save_to_ai_memory(msg_id)
#                     ai_read_memory.add(msg_id)
#                     processed_count += 1
#                     print(f"💾 Marked as Read in AI Memory: {msg_id}\n")
#                     print("=" * 80 + "\n")
                    
#                 except Exception as single_mail_error:
#                     print(f"⚠️ Error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
#                     import traceback
#                     traceback.print_exc()
#                     continue
        
#         except Exception as folder_error:
#             print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
#             import traceback
#             traceback.print_exc()
#             continue

#     mail.logout()
#     print("=" * 80)
#     print(f"✅ IMAP connection closed.")
#     print(f"📊 Processed {processed_count} email(s) in this run.")
#     print(f"📂 Total processed emails in memory: {len(ai_read_memory)}")


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



# import imaplib
# import email
# from email.header import decode_header
# import email.utils
# import os
# import urllib.parse
# import base64
# import io
# import re # Import the regular expression module
# import requests
# from datetime import datetime
# import pytz
# from PIL import Image, ImageDraw, ImageFont

# # --- Environment Variables ---
# # Ensure NTFY_TOPIC contains ONLY the topic name, e.g., "my_topic"
# # NOT the full URL like "https://ntfy.sh/my_topic"
# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# NTFY_TOPIC_NAME = os.getenv("NTFY_TOPIC") # Renamed for clarity

# if not NTFY_TOPIC_NAME or NTFY_TOPIC_NAME.startswith("http"):
#     print("Error: NTFY_TOPIC environment variable must contain only the topic name (e.g., 'mytopic'). It currently seems incorrect.")
#     exit(1)

# MEMORY_FILE = "processed_emails.txt"

# def load_ai_memory():
#     """Loads handled email tracking strings from the local file storage."""
#     if not os.path.exists(MEMORY_FILE):
#         return set()
#     with open(MEMORY_FILE, "r", encoding="utf-8") as f:
#         return set(line.strip() for line in f if line.strip())

# def save_to_ai_memory(msg_id):
#     """Saves a processed message hash permanently onto the local file."""
#     with open(MEMORY_FILE, "a", encoding="utf-8") as f:
#         f.write(f"{msg_id}\n")

# def text_to_image_bytes(sender, subject, body):
#     """Renders text data onto an image canvas in system memory."""
#     width = 800
#     height = 1000
#     image = Image.new("RGB", (width, height), color=(245, 245, 245))
#     draw = ImageDraw.Draw(image)
    
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
#                 "options": { "temperature": 0.1 }
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
            
#             if content_type == "text/plain" and "attachment" not in content_disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     return payload.decode(errors="ignore").strip()
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             return payload.decode(errors="ignore").strip()
            
#     return ""

# def extract_emails_from_text(text):
#     """
#     Extracts email addresses from a given text string using a regular expression.
#     This function finds all substrings matching the typical email pattern.
#     """
#     # Regular expression pattern for email addresses
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     # Find all matches in the provided text
#     found_emails = re.findall(email_pattern, text)
#     # Return a list of unique email addresses found
#     return list(set(found_emails)) # Using set to remove potential duplicates


# def check_email():
#     """Main scanning connection engine exploring all folders sequentially."""
#     try:
#         print("🔐 Connecting to Gmail IMAP server...")
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         print("✅ Successfully connected to Gmail!")
#     except Exception as conn_error:
#         print(f"❌ IMAP Connection Failed: {str(conn_error)}")
#         return
    
#     try:
#         mail.login(EMAIL_USER, EMAIL_PASS)
#         print("✅ Successfully logged in!")
#     except Exception as login_error:
#         print(f"❌ Login Failed: {str(login_error)}")
#         mail.logout()
#         return

#     user_tz = pytz.timezone("Asia/Kolkata") 
#     today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
#     print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

#     # Load the set of already processed message IDs ONCE at the beginning
#     ai_read_memory = load_ai_memory()
#     print(f"📂 Loaded {len(ai_read_memory)} previously processed email IDs from memory.")

#     target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
#     processed_count = 0

#     for folder in target_folders:
#         try:
#             print(f"📂 Opening Folder Location: {folder}...")
#             status, _ = mail.select(f'"{folder}"', readonly=True)
#             if status != "OK":
#                 print(f"⚠️ Could not select folder: {folder}")
#                 continue
            
#             status, messages = mail.search(None, 'SINCE', today_imap_str)
#             if status != "OK" or not messages:
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             raw_bytes = messages[0] if isinstance(messages, list) else messages
#             if not raw_bytes or raw_bytes == b'':
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             email_ids = raw_bytes.split()
#             print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

#             # --- PROCESS ONLY THE FIRST EMAIL FOUND ---
#             email_processed_in_this_run = False
#             for e_id in email_ids:
#                 if email_processed_in_this_run:
#                     print("   ℹ️  Stopping after processing one email in this run.")
#                     break # Exit the email loop after one iteration

#                 print(f"--- Processing Email ID: {e_id.decode()} ---")
#                 try:
#                     status, msg_data = mail.fetch(e_id, "(RFC822)")
#                     if status != "OK":
#                         print(f"   ⚠️ Fetch failed for ID {e_id.decode()}")
#                         continue
                    
#                     msg_content = None
#                     if msg_data and isinstance(msg_data, list):
#                         for response_part in msg_data:
#                             if isinstance(response_part, tuple):
#                                 msg_content = response_part[1]
#                                 break
#                             elif isinstance(response_part, bytes):
#                                 msg_content = response_part
#                                 break
                    
#                     if msg_content is None:
#                         print(f"   ⚠️ No content retrieved for ID {e_id.decode()}")
#                         continue
                    
#                     try:
#                         msg = email.message_from_bytes(msg_content)
#                     except Exception as parse_error:
#                         print(f"   ⚠️ Error parsing message for ID {e_id.decode()}: {parse_error}")
#                         continue
                    
#                     msg_id = msg.get("Message-ID", "")
#                     if msg_id:
#                         msg_id = msg_id.strip("< >")
#                     else:
#                         msg_id = f"generated-id-{e_id.decode()}"
                    
#                     # Check if this specific email ID has already been processed
#                     if msg_id in ai_read_memory:
#                         print(f"   💾 Skipping {msg_id}, already processed.")
#                         continue
#                     else:
#                         print(f"   🆕 First time seeing ID: {msg_id}")

#                     from_header = msg.get("From", "Unknown Sender")
#                     raw_date = msg.get("Date", "")
                    
#                     try:
#                         # 1. Parse the raw date string from the email header
#                         parsed_date = email.utils.parsedate_to_datetime(raw_date)
                        
#                         # 2. Convert it to Indian Standard Time (IST)
#                         ist_date = parsed_date.astimezone(user_tz)
                        
#                         # 3. Format it to show only the time (or include date if you prefer)
#                         formatted_time = ist_date.strftime("%H:%M:%S") 
                        
#                     except Exception:
#                         formatted_time = "Unknown Time"

#                     # --- FIX FOR SUBJECT DECODING ---
#                     raw_subject = msg.get("Subject", "No Subject")
#                     decoded_parts = decode_header(raw_subject)
                    
#                     if decoded_parts:
#                         part, encoding = decoded_parts[0]
#                         if isinstance(part, bytes):
#                             subject = part.decode(encoding or 'utf-8', errors='ignore')
#                         else:
#                             subject = part
#                     else:
#                         subject = "No Subject"
#                     # --- END FIX ---

#                     print(f"   📥 [{formatted_time} IST] Processing Single Mail:")                    
#                     print(f"      From: {from_header}")
#                     print(f"      Subject: {subject}")
                    
#                     body_text = get_email_body(msg)
#                     if not body_text:
#                         print("      ⚠️ Skipping processing: No readable text body found.\n")
#                         # Even if there's no body, we consider it 'processed' to avoid re-scanning
#                         save_to_ai_memory(msg_id)
#                         ai_read_memory.add(msg_id) # Update local memory set
#                         processed_count += 1
#                         print(f"      💾 Marked as Read in AI Memory (no body): {msg_id}\n")
#                         print("=" * 80 + "\n")
#                         email_processed_in_this_run = True # Mark that an email was handled
#                         continue # Move to the next email in the loop, but then break the loop

#                     # --- EXTRACT EMAILS FROM THE BODY ---
#                     extracted_emails = extract_emails_from_text(body_text)
#                     print(f"      Emails found in body: {extracted_emails}") # Print the found emails

#                     print("      🖼️ Transforming text fields into secure image matrix canvas...")
#                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
#                     print("      🧠 Passing image matrix directly to Qwen2.5-VL...")
#                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
#                     print(f"\n      🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
#                     encoded_id = urllib.parse.quote(msg_id)
#                     # Example placeholder link
#                     gmail_url = f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{encoded_id}" # Example link
#                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
#                     # Include extracted emails in the alert if any were found
#                     alert_body = ai_analysis
#                     if extracted_emails:
#                          alert_body += f"\n\n📧 Emails found in body: {', '.join(extracted_emails)}"

#                     # Attempt to send the ntfy alert
#                     try:
#                         send_ntfy_alert(alert_body, gmail_url, priority) # Send the modified alert
#                         print("      ✅ Analysis dispatched via ntfy successfully.")
#                     except Exception as ntfy_error:
#                         print(f"      ❌ Ntfy dispatch failed for {msg_id}: {ntfy_error}")
#                         # Decide whether to save the ID if ntfy fails. For now, let's save it anyway,
#                         # assuming the core processing (analysis) was attempted.
#                         pass # Error already printed, continue with saving.

#                     # --- CRITICAL: Save the ID AFTER attempting processing ---
#                     save_to_ai_memory(msg_id)
#                     ai_read_memory.add(msg_id) # Update local memory set
#                     processed_count += 1
#                     print(f"      💾 Marked as Read in AI Memory: {msg_id}\n")
#                     print("=" * 80 + "\n")
#                     email_processed_in_this_run = True # Mark that an email was handled
                    
#                 except Exception as single_mail_error:
#                     print(f"      ⚠️ Unexpected error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
#                     import traceback
#                     traceback.print_exc()
#                     continue # Continue to the next email in the loop, but then break the loop
        
#         except Exception as folder_error:
#             print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
#             import traceback
#             traceback.print_exc()
#             continue # Continue to the next folder in the loop

#     mail.logout()
#     print("=" * 80)
#     print(f"✅ IMAP connection closed.")
#     print(f"📊 Processed {processed_count} email(s) in this run.")
#     print(f"📂 Total processed emails in memory file ({MEMORY_FILE}): {len(load_ai_memory())}") # Reload to confirm final count


# def send_ntfy_alert(ai_analysis, email_url, priority):
#     # Construct the URL correctly using the topic name
#     url = f"https://ntfy.sh/{NTFY_TOPIC_NAME.strip('/')}" # Ensure NTFY_TOPIC_NAME is just the name
#     headers = {
#         "Title": "👁️ Qwen Vision Secretary Brief",
#         "Priority": priority,
#         "Tags": "camera,robot",
#         "Click": email_url # This header allows ntfy apps to open a URL on tap
#     }
#     # Ensure the message body is correctly encoded as UTF-8
#     message_body = f"{ai_analysis}\n\n👉 Tap this notification to open email in Gmail."
#     # Use requests.post to send the data, explicitly encoding the body as UTF-8
#     response = requests.post(url, data=message_body.encode('utf-8'), headers=headers) # Explicitly encode data
#     # Check the response status code
#     if response.status_code != 200:
#          print(f"   ❌ Ntfy request failed with status {response.status_code}: {response.text}")
#          raise requests.HTTPError(f"Ntfy returned status {response.status_code}")
#     print(f"   📬 Sent ntfy alert for topic '{NTFY_TOPIC_NAME}'")


# if __name__ == "__main__":
#     check_email()









# import imaplib
# import email
# from email.header import decode_header
# import email.utils
# import os
# import urllib.parse
# import base64
# import io
# import re # Import the regular expression module
# import requests
# from datetime import datetime
# import pytz
# from PIL import Image, ImageDraw, ImageFont

# # --- Environment Variables ---
# # Ensure NTFY_TOPIC contains ONLY the topic name, e.g., "my_topic"
# # NOT the full URL like "https://ntfy.sh/my_topic"
# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# NTFY_TOPIC_NAME = os.getenv("NTFY_TOPIC") # Renamed for clarity

# if not NTFY_TOPIC_NAME or NTFY_TOPIC_NAME.startswith("http"):
#     print("Error: NTFY_TOPIC environment variable must contain only the topic name (e.g., 'mytopic'). It currently seems incorrect.")
#     exit(1)

# MEMORY_FILE = "processed_emails.txt"

# def load_ai_memory():
#     """Loads handled email tracking strings from the local file storage."""
#     if not os.path.exists(MEMORY_FILE):
#         return set()
#     with open(MEMORY_FILE, "r", encoding="utf-8") as f:
#         return set(line.strip() for line in f if line.strip())

# def save_to_ai_memory(msg_id):
#     """Saves a processed message hash permanently onto the local file."""
#     with open(MEMORY_FILE, "a", encoding="utf-8") as f:
#         f.write(f"{msg_id}\n")

# def text_to_image_bytes(sender, subject, body):
#     """Renders text data onto an image canvas in system memory."""
#     width = 800
#     height = 1000
#     image = Image.new("RGB", (width, height), color=(245, 245, 245))
#     draw = ImageDraw.Draw(image)
    
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
#                 "options": { "temperature": 0.1 }
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
            
#             if content_type == "text/plain" and "attachment" not in content_disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     return payload.decode(errors="ignore").strip()
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             return payload.decode(errors="ignore").strip()
            
#     return ""

# def extract_emails_from_text(text):
#     """
#     Extracts email addresses from a given text string using a regular expression.
#     This function finds all substrings matching the typical email pattern.
#     """
#     # Regular expression pattern for email addresses
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     # Find all matches in the provided text
#     found_emails = re.findall(email_pattern, text)
#     # Return a list of unique email addresses found
#     return list(set(found_emails)) # Using set to remove potential duplicates


# def check_email():
#     """Main scanning connection engine exploring all folders sequentially."""
#     try:
#         print("🔐 Connecting to Gmail IMAP server...")
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         print("✅ Successfully connected to Gmail!")
#     except Exception as conn_error:
#         print(f"❌ IMAP Connection Failed: {str(conn_error)}")
#         return
    
#     try:
#         mail.login(EMAIL_USER, EMAIL_PASS)
#         print("✅ Successfully logged in!")
#     except Exception as login_error:
#         print(f"❌ Login Failed: {str(login_error)}")
#         mail.logout()
#         return

#     user_tz = pytz.timezone("Asia/Kolkata") 
#     today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
#     print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

#     # Load the set of already processed message IDs ONCE at the beginning
#     ai_read_memory = load_ai_memory()
#     print(f"📂 Loaded {len(ai_read_memory)} previously processed email IDs from memory.")

#     target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
#     processed_count = 0

#     for folder in target_folders:
#         try:
#             print(f"📂 Opening Folder Location: {folder}...")
#             status, _ = mail.select(f'"{folder}"', readonly=True)
#             if status != "OK":
#                 print(f"⚠️ Could not select folder: {folder}")
#                 continue
            
#             status, messages = mail.search(None, 'SINCE', today_imap_str)
#             if status != "OK" or not messages:
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             raw_bytes = messages[0] if isinstance(messages, list) else messages
#             if not raw_bytes or raw_bytes == b'':
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             email_ids = raw_bytes.split()
#             print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

#             # --- PROCESS ONLY THE FIRST EMAIL FOUND ---
#             email_processed_in_this_run = False
#             for e_id in email_ids:
#                 if email_processed_in_this_run:
#                     print("   ℹ️  Stopping after processing one email in this run.")
#                     break # Exit the email loop after one iteration

#                 print(f"--- Processing Email ID: {e_id.decode()} ---")
#                 try:
#                     status, msg_data = mail.fetch(e_id, "(RFC822)")
#                     if status != "OK":
#                         print(f"   ⚠️ Fetch failed for ID {e_id.decode()}")
#                         continue
                    
#                     msg_content = None
#                     if msg_data and isinstance(msg_data, list):
#                         for response_part in msg_data:
#                             if isinstance(response_part, tuple):
#                                 msg_content = response_part[1]
#                                 break
#                             elif isinstance(response_part, bytes):
#                                 msg_content = response_part
#                                 break
                    
#                     if msg_content is None:
#                         print(f"   ⚠️ No content retrieved for ID {e_id.decode()}")
#                         continue
                    
#                     try:
#                         msg = email.message_from_bytes(msg_content)
#                     except Exception as parse_error:
#                         print(f"   ⚠️ Error parsing message for ID {e_id.decode()}: {parse_error}")
#                         continue
                    
#                     msg_id = msg.get("Message-ID", "")
#                     if msg_id:
#                         msg_id = msg_id.strip("< >")
#                     else:
#                         msg_id = f"generated-id-{e_id.decode()}"
                    
#                     # Check if this specific email ID has already been processed
#                     if msg_id in ai_read_memory:
#                         print(f"   💾 Skipping {msg_id}, already processed.")
#                         continue
#                     else:
#                         print(f"   🆕 First time seeing ID: {msg_id}")

#                     from_header = msg.get("From", "Unknown Sender")
#                     raw_date = msg.get("Date", "")
                    
#                     try:
#                         # 1. Parse the raw date string from the email header
#                         parsed_date = email.utils.parsedate_to_datetime(raw_date)
                        
#                         # 2. Convert it to Indian Standard Time (IST)
#                         ist_date = parsed_date.astimezone(user_tz)
                        
#                         # 3. Format it to show only the time (or include date if you prefer)
#                         formatted_time = ist_date.strftime("%H:%M:%S") 
                        
#                     except Exception:
#                         formatted_time = "Unknown Time"

#                     # --- FIX FOR SUBJECT DECODING ---
#                     raw_subject = msg.get("Subject", "No Subject")
#                     decoded_parts = decode_header(raw_subject)
                    
#                     if decoded_parts:
#                         part, encoding = decoded_parts[0]
#                         if isinstance(part, bytes):
#                             subject = part.decode(encoding or 'utf-8', errors='ignore')
#                         else:
#                             subject = part
#                     else:
#                         subject = "No Subject"
#                     # --- END FIX ---

#                     print(f"   📥 [{formatted_time} IST] Processing Single Mail:")                    
#                     print(f"      From: {from_header}")
#                     print(f"      Subject: {subject}")
                    
#                     body_text = get_email_body(msg)
#                     if not body_text:
#                         print("      ⚠️ Skipping processing: No readable text body found.\n")
#                         # Even if there's no body, we consider it 'processed' to avoid re-scanning
#                         save_to_ai_memory(msg_id)
#                         ai_read_memory.add(msg_id) # Update local memory set
#                         processed_count += 1
#                         print(f"      💾 Marked as Read in AI Memory (no body): {msg_id}\n")
#                         print("=" * 80 + "\n")
#                         email_processed_in_this_run = True # Mark that an email was handled
#                         continue # Move to the next email in the loop, but then break the loop

#                     # --- EXTRACT EMAILS FROM THE BODY ---
#                     extracted_emails = extract_emails_from_text(body_text)
#                     print(f"      Emails found in body: {extracted_emails}") # Print the found emails

#                     print("      🖼️ Transforming text fields into secure image matrix canvas...")
#                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
#                     print("      🧠 Passing image matrix directly to Qwen2.5-VL...")
#                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
#                     print(f"\n      🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
#                     encoded_id = urllib.parse.quote(msg_id)
#                     # Example placeholder link
#                     gmail_url = f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{encoded_id}" # Example link
#                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
#                     # Include extracted emails in the alert if any were found
#                     alert_body = ai_analysis
#                     if extracted_emails:
#                          alert_body += f"\n\n📧 Emails found in body: {', '.join(extracted_emails)}"

#                     # Attempt to send the ntfy alert - wrap the *call* in a broad try-except
#                     try:
#                         send_ntfy_alert(alert_body, gmail_url, priority) # Send the modified alert
#                         print("      ✅ Analysis dispatched via ntfy successfully.")
#                     except Exception as ntfy_error: # Catch any error during the ntfy call
#                         print(f"      ❌ Ntfy dispatch failed for {msg_id} (any error): {ntfy_error}")
#                         # Decide whether to save the ID if ntfy fails. For now, let's save it anyway,
#                         # assuming the core processing (analysis) was attempted.
#                         pass # Error already printed, continue with saving.

#                     # --- CRITICAL: Save the ID AFTER attempting processing ---
#                     save_to_ai_memory(msg_id)
#                     ai_read_memory.add(msg_id) # Update local memory set
#                     processed_count += 1
#                     print(f"      💾 Marked as Read in AI Memory: {msg_id}\n")
#                     print("=" * 80 + "\n")
#                     email_processed_in_this_run = True # Mark that an email was handled
                    
#                 except Exception as single_mail_error:
#                     print(f"      ⚠️ Unexpected error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
#                     import traceback
#                     traceback.print_exc()
#                     continue # Continue to the next email in the loop, but then break the loop
        
#         except Exception as folder_error:
#             print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
#             import traceback
#             traceback.print_exc()
#             continue # Continue to the next folder in the loop

#     mail.logout()
#     print("=" * 80)
#     print(f"✅ IMAP connection closed.")
#     print(f"📊 Processed {processed_count} email(s) in this run.")
#     print(f"📂 Total processed emails in memory file ({MEMORY_FILE}): {len(load_ai_memory())}") # Reload to confirm final count


# def send_ntfy_alert(ai_analysis, email_url, priority):
#     # Construct the URL correctly using the topic name
#     url = f"https://ntfy.sh/{NTFY_TOPIC_NAME.strip('/')}" # Ensure NTFY_TOPIC_NAME is just the name
#     # Clean headers containing only standard text characters
#     # Avoid deriving header values directly from potentially problematic ai_analysis
#     safe_priority = priority if priority in ['low', 'default', 'high', 'urgent'] else 'default'
#     headers = {
#         "Title": "👁️ Qwen Vision Secretary Brief", # Safe static title
#         "Priority": safe_priority,
#         "Click": email_url # This header allows ntfy apps to open a URL on tap
#     }
#     # Emojis are generally okay in the message body
#     message_body = f"{ai_analysis}\n\n👉 Tap this notification to open email in Gmail."
#     # Use requests.post to send the data, explicitly encoding the body as UTF-8
#     # Add a timeout for reliability
#     response = requests.post(url, data=message_body.encode('utf-8'), headers=headers, timeout=20)
#     # Check the response status code
#     if response.status_code != 200:
#          print(f"   ❌ Ntfy request failed with status {response.status_code}: {response.text}")
#          raise requests.HTTPError(f"Ntfy returned status {response.status_code}")
#     print(f"   📬 Sent ntfy alert for topic '{NTFY_TOPIC_NAME}'")


# if __name__ == "__main__":
#     check_email()






# import imaplib
# import email
# from email.header import decode_header
# import email.utils
# import os
# import urllib.parse
# import base64
# import io
# import re # Import the regular expression module
# import requests
# from datetime import datetime
# import pytz
# from PIL import Image, ImageDraw, ImageFont
# import unicodedata # Import for text normalization/sanitization

# # --- Environment Variables ---
# # Ensure NTFY_TOPIC contains ONLY the topic name, e.g., "my_topic"
# # NOT the full URL like "https://ntfy.sh/my_topic"
# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")
# NTFY_TOPIC_NAME = os.getenv("NTFY_TOPIC") # Renamed for clarity

# if not NTFY_TOPIC_NAME or NTFY_TOPIC_NAME.startswith("http"):
#     print("Error: NTFY_TOPIC environment variable must contain only the topic name (e.g., 'mytopic'). It currently seems incorrect.")
#     exit(1)

# MEMORY_FILE = "processed_emails.txt"

# def load_ai_memory():
#     """Loads handled email tracking strings from the local file storage."""
#     if not os.path.exists(MEMORY_FILE):
#         return set()
#     with open(MEMORY_FILE, "r", encoding="utf-8") as f:
#         return set(line.strip() for line in f if line.strip())

# def save_to_ai_memory(msg_id):
#     """Saves a processed message hash permanently onto the local file."""
#     with open(MEMORY_FILE, "a", encoding="utf-8") as f:
#         f.write(f"{msg_id}\n")

# def text_to_image_bytes(sender, subject, body):
#     """Renders text data onto an image canvas in system memory."""
#     width = 800
#     height = 1000
#     image = Image.new("RGB", (width, height), color=(245, 245, 245))
#     draw = ImageDraw.Draw(image)
    
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
#                 "options": { "temperature": 0.1 }
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
            
#             if content_type == "text/plain" and "attachment" not in content_disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     return payload.decode(errors="ignore").strip()
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             return payload.decode(errors="ignore").strip()
            
#     return ""

# def extract_emails_from_text(text):
#     """
#     Extracts email addresses from a given text string using a regular expression.
#     This function finds all substrings matching the typical email pattern.
#     """
#     # Regular expression pattern for email addresses
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     # Find all matches in the provided text
#     found_emails = re.findall(email_pattern, text)
#     # Return a list of unique email addresses found
#     return list(set(found_emails)) # Using set to remove potential duplicates


# def check_email():
#     """Main scanning connection engine exploring all folders sequentially."""
#     try:
#         print("🔐 Connecting to Gmail IMAP server...")
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         print("✅ Successfully connected to Gmail!")
#     except Exception as conn_error:
#         print(f"❌ IMAP Connection Failed: {str(conn_error)}")
#         return
    
#     try:
#         mail.login(EMAIL_USER, EMAIL_PASS)
#         print("✅ Successfully logged in!")
#     except Exception as login_error:
#         print(f"❌ Login Failed: {str(login_error)}")
#         mail.logout()
#         return

#     user_tz = pytz.timezone("Asia/Kolkata") 
#     today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
#     print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

#     # Load the set of already processed message IDs ONCE at the beginning
#     ai_read_memory = load_ai_memory()
#     print(f"📂 Loaded {len(ai_read_memory)} previously processed email IDs from memory.")

#     target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
#     processed_count = 0

#     for folder in target_folders:
#         try:
#             print(f"📂 Opening Folder Location: {folder}...")
#             status, _ = mail.select(f'"{folder}"', readonly=True)
#             if status != "OK":
#                 print(f"⚠️ Could not select folder: {folder}")
#                 continue
            
#             status, messages = mail.search(None, 'SINCE', today_imap_str)
#             if status != "OK" or not messages:
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             raw_bytes = messages[0] if isinstance(messages, list) else messages
#             if not raw_bytes or raw_bytes == b'':
#                 print(f"🏖️ No emails found in {folder} from today.")
#                 continue

#             email_ids = raw_bytes.split()
#             print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

#             # --- PROCESS ONLY THE FIRST EMAIL FOUND ---
#             email_processed_in_this_run = False
#             for e_id in email_ids:
#                 if email_processed_in_this_run:
#                     print("   ℹ️  Stopping after processing one email in this run.")
#                     break # Exit the email loop after one iteration

#                 print(f"--- Processing Email ID: {e_id.decode()} ---")
#                 try:
#                     status, msg_data = mail.fetch(e_id, "(RFC822)")
#                     if status != "OK":
#                         print(f"   ⚠️ Fetch failed for ID {e_id.decode()}")
#                         continue
                    
#                     msg_content = None
#                     if msg_data and isinstance(msg_data, list):
#                         for response_part in msg_data:
#                             if isinstance(response_part, tuple):
#                                 msg_content = response_part[1]
#                                 break
#                             elif isinstance(response_part, bytes):
#                                 msg_content = response_part
#                                 break
                    
#                     if msg_content is None:
#                         print(f"   ⚠️ No content retrieved for ID {e_id.decode()}")
#                         continue
                    
#                     try:
#                         msg = email.message_from_bytes(msg_content)
#                     except Exception as parse_error:
#                         print(f"   ⚠️ Error parsing message for ID {e_id.decode()}: {parse_error}")
#                         continue
                    
#                     msg_id = msg.get("Message-ID", "")
#                     if msg_id:
#                         msg_id = msg_id.strip("< >")
#                     else:
#                         msg_id = f"generated-id-{e_id.decode()}"
                    
#                     # Check if this specific email ID has already been processed
#                     if msg_id in ai_read_memory:
#                         print(f"   💾 Skipping {msg_id}, already processed.")
#                         continue
#                     else:
#                         print(f"   🆕 First time seeing ID: {msg_id}")

#                     from_header = msg.get("From", "Unknown Sender")
#                     raw_date = msg.get("Date", "")
                    
#                     try:
#                         # 1. Parse the raw date string from the email header
#                         parsed_date = email.utils.parsedate_to_datetime(raw_date)
                        
#                         # 2. Convert it to Indian Standard Time (IST)
#                         ist_date = parsed_date.astimezone(user_tz)
                        
#                         # 3. Format it to show only the time (or include date if you prefer)
#                         formatted_time = ist_date.strftime("%H:%M:%S") 
                        
#                     except Exception:
#                         formatted_time = "Unknown Time"

#                     # --- FIX FOR SUBJECT DECODING ---
#                     raw_subject = msg.get("Subject", "No Subject")
#                     decoded_parts = decode_header(raw_subject)
                    
#                     if decoded_parts:
#                         part, encoding = decoded_parts[0]
#                         if isinstance(part, bytes):
#                             subject = part.decode(encoding or 'utf-8', errors='ignore')
#                         else:
#                             subject = part
#                     else:
#                         subject = "No Subject"
#                     # --- END FIX ---

#                     print(f"   📥 [{formatted_time} IST] Processing Single Mail:")                    
#                     print(f"      From: {from_header}")
#                     print(f"      Subject: {subject}")
                    
#                     body_text = get_email_body(msg)
#                     if not body_text:
#                         print("      ⚠️ Skipping processing: No readable text body found.\n")
#                         # Even if there's no body, we consider it 'processed' to avoid re-scanning
#                         save_to_ai_memory(msg_id)
#                         ai_read_memory.add(msg_id) # Update local memory set
#                         processed_count += 1
#                         print(f"      💾 Marked as Read in AI Memory (no body): {msg_id}\n")
#                         print("=" * 80 + "\n")
#                         email_processed_in_this_run = True # Mark that an email was handled
#                         continue # Move to the next email in the loop, but then break the loop

#                     # --- EXTRACT EMAILS FROM THE BODY ---
#                     extracted_emails = extract_emails_from_text(body_text)
#                     print(f"      Emails found in body: {extracted_emails}") # Print the found emails

#                     print("      🖼️ Transforming text fields into secure image matrix canvas...")
#                     img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
#                     print("      🧠 Passing image matrix directly to Qwen2.5-VL...")
#                     ai_analysis = analyze_image_with_qwen(img_bytes)
                    
#                     print(f"\n      🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
#                     encoded_id = urllib.parse.quote(msg_id)
#                     # Example placeholder link
#                     gmail_url = f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{encoded_id}" # Example link
#                     priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
#                     # Include extracted emails in the alert if any were found
#                     alert_body = ai_analysis
#                     if extracted_emails:
#                          alert_body += f"\n\n📧 Emails found in body: {', '.join(extracted_emails)}"

#                     # Attempt to send the ntfy alert - wrap the *call* in a broad try-except
#                     try:
#                         send_ntfy_alert(alert_body, gmail_url, priority) # Send the modified alert
#                         print("      ✅ Analysis dispatched via ntfy successfully.")
#                     except Exception as ntfy_error: # Catch any error during the ntfy call
#                         print(f"      ❌ Ntfy dispatch failed for {msg_id} (any error): {ntfy_error}")
#                         # Decide whether to save the ID if ntfy fails. For now, let's save it anyway,
#                         # assuming the core processing (analysis) was attempted.
#                         pass # Error already printed, continue with saving.

#                     # --- CRITICAL: Save the ID AFTER attempting processing ---
#                     save_to_ai_memory(msg_id)
#                     ai_read_memory.add(msg_id) # Update local memory set
#                     processed_count += 1
#                     print(f"      💾 Marked as Read in AI Memory: {msg_id}\n")
#                     print("=" * 80 + "\n")
#                     email_processed_in_this_run = True # Mark that an email was handled
                    
#                 except Exception as single_mail_error:
#                     print(f"      ⚠️ Unexpected error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
#                     import traceback
#                     traceback.print_exc()
#                     continue # Continue to the next email in the loop, but then break the loop
        
#         except Exception as folder_error:
#             print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
#             import traceback
#             traceback.print_exc()
#             continue # Continue to the next folder in the loop

#     mail.logout()
#     print("=" * 80)
#     print(f"✅ IMAP connection closed.")
#     print(f"📊 Processed {processed_count} email(s) in this run.")
#     print(f"📂 Total processed emails in memory file ({MEMORY_FILE}): {len(load_ai_memory())}") # Reload to confirm final count


# def send_ntfy_alert(ai_analysis, email_url, priority):
#     # --- Execution (Following the example pattern closely) ---
#     url = f"https://ntfy.sh/{NTFY_TOPIC_NAME.strip('/')}" # Construct the URL correctly using the topic name

#     # Clean headers containing only standard text characters
#     # Derive priority from input, ensure it's safe
#     safe_priority = priority if priority in ['low', 'default', 'high', 'urgent'] else 'default'
#     headers = {
#         "Title": "👁️ Qwen Vision Secretary Brief", # Safe static title
#         "Priority": safe_priority,
#         "Click": email_url # This header allows ntfy apps to open a URL on tap
#     }

#     # Emojis are generally okay in the message body text
#     message_body = f"{ai_analysis}\n\n👉 Tap this notification to open email in Gmail."

#     # --- Tier 1: Attempt with original data ---
#     try:
#         response = requests.post(url, data=message_body.encode('utf-8'), headers=headers, timeout=20)
#         if response.status_code == 200:
#             print(f"   📬 Sent ntfy alert for topic '{NTFY_TOPIC_NAME}' successfully (Tier 1).")
#             return # Success, exit the function
#         else:
#             print(f"   ❌ Ntfy request (Tier 1) failed with status {response.status_code}: {response.text}")
#             # Proceed to Tier 2 if status code is not 200
#     except Exception as e1:
#         print(f"   ❌ Ntfy request (Tier 1) failed due to an exception: {e1}")
#         # Proceed to Tier 2 if the request raises an exception (like encoding error)

#     # --- Tier 2: Sanitize and retry ---
#     print("   Attempting fallback (Tier 2) with sanitized data...")
#     # Sanitize the message body and headers by normalizing and removing non-ASCII chars
#     try:
#         # Normalize the text (NFKD decomposes characters)
#         normalized_body = unicodedata.normalize('NFKD', message_body)
#         normalized_title = unicodedata.normalize('NFKD', headers["Title"])
#         # Encode to ASCII, ignoring characters that can't be encoded
#         ascii_body = normalized_body.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
#         ascii_title = normalized_title.encode('ascii', errors='ignore').decode('ascii', errors='ignore')

#         # Create fallback headers and message
#         fallback_headers = {
#             "Title": ascii_title,
#             "Priority": safe_priority,
#             "Click": email_url
#         }
#         fallback_message = f"ALERT BODY SANITIZED DUE TO ENCODING ISSUES.\n\n{ascii_body}"

#         # Retry the request with sanitized data
#         response_fallback = requests.post(url, data=fallback_message.encode('utf-8'), headers=fallback_headers, timeout=20)
#         if response_fallback.status_code == 200:
#             print(f"   📬 Sent ntfy alert for topic '{NTFY_TOPIC_NAME}' successfully (Tier 2 - Fallback).")
#             return # Success with fallback, exit the function
#         else:
#             print(f"   ❌ Ntfy request (Tier 2 - Fallback) failed with status {response_fallback.status_code}: {response_fallback.text}")
#     except Exception as e2:
#         print(f"   ❌ Ntfy request (Tier 2 - Fallback) failed due to an exception: {e2}")

#     # --- Tier 3: Ultimate Fallback ---
#     print("   Attempting ultimate fallback (Tier 3) with basic message...")
#     # If both Tiers 1 and 2 fail, send a very basic message
#     ultimate_fallback_message = "Email processing completed, but AI analysis could not be sent via ntfy due to encoding/network issues."
#     ultimate_fallback_headers = {
#         "Title": "Email Processing Alert - Fallback",
#         "Priority": "default",
#         "Click": email_url
#     }
#     try:
#         response_ultimate = requests.post(url, data=ultimate_fallback_message.encode('utf-8'), headers=ultimate_fallback_headers, timeout=20)
#         if response_ultimate.status_code == 200:
#              print(f"   📬 Sent basic ntfy alert for topic '{NTFY_TOPIC_NAME}' successfully (Tier 3 - Ultimate Fallback).")
#         else:
#              print(f"   ❌ Ultimate fallback ntfy request failed with status {response_ultimate.status_code}: {response_ultimate.text}")
#     except Exception as e3:
#         print(f"   ❌ Ultimate fallback ntfy request failed due to an exception: {e3}")

#     # If all tiers fail, raise an error to be caught by the caller's exception handler
#     raise RuntimeError("All ntfy sending tiers failed.")


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
import re # Import the regular expression module
import requests
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
import unicodedata # Import for text normalization/sanitization

# --- Environment Variables ---
# Ensure NTFY_TOPIC contains ONLY the topic name, e.g., "my_topic"
# NOT the full URL like "https://ntfy.sh/my_topic"
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
NTFY_TOPIC_NAME = os.getenv("NTFY_TOPIC") # Renamed for clarity

if not NTFY_TOPIC_NAME or NTFY_TOPIC_NAME.startswith("http"):
    print("Error: NTFY_TOPIC environment variable must contain only the topic name (e.g., 'mytopic'). It currently seems incorrect.")
    exit(1)

MEMORY_FILE = "processed_emails.txt"

def load_ai_memory():
    """Loads handled email tracking strings from the local file storage."""
    if not os.path.exists(MEMORY_FILE):
        return set()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_to_ai_memory(msg_id):
    """Saves a processed message hash permanently onto the local file."""
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg_id}\n")

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
    """Recursively walks email structure to find and extract plain text."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore").strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore").strip()
            
    return ""

def extract_emails_from_text(text):
    """
    Extracts email addresses from a given text string using a regular expression.
    This function finds all substrings matching the typical email pattern.
    """
    # Regular expression pattern for email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # Find all matches in the provided text
    found_emails = re.findall(email_pattern, text)
    # Return a list of unique email addresses found
    return list(set(found_emails)) # Using set to remove potential duplicates


def check_email():
    """Main scanning connection engine exploring all folders sequentially."""
    try:
        print("🔐 Connecting to Gmail IMAP server...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        print("✅ Successfully connected to Gmail!")
    except Exception as conn_error:
        print(f"❌ IMAP Connection Failed: {str(conn_error)}")
        return
    
    try:
        mail.login(EMAIL_USER, EMAIL_PASS)
        print("✅ Successfully logged in!")
    except Exception as login_error:
        print(f"❌ Login Failed: {str(login_error)}")
        mail.logout()
        return

    user_tz = pytz.timezone("Asia/Kolkata") 
    today_imap_str = datetime.now(user_tz).strftime("%d-%b-%Y")
    print(f"📅 Scanning all mail categories initialized for date: {today_imap_str}\n")

    # Load the set of already processed message IDs ONCE at the beginning
    ai_read_memory = load_ai_memory()
    print(f"📂 Loaded {len(ai_read_memory)} previously processed email IDs from memory.")

    target_folders = ["[Gmail]/All Mail", "[Gmail]/Spam"]
    processed_count = 0

    for folder in target_folders:
        try:
            print(f"📂 Opening Folder Location: {folder}...")
            status, _ = mail.select(f'"{folder}"', readonly=True)
            if status != "OK":
                print(f"⚠️ Could not select folder: {folder}")
                continue
            
            status, messages = mail.search(None, 'SINCE', today_imap_str)
            if status != "OK" or not messages:
                print(f"🏖️ No emails found in {folder} from today.")
                continue

            raw_bytes = messages[0] if isinstance(messages, list) else messages
            if not raw_bytes or raw_bytes == b'':
                print(f"🏖️ No emails found in {folder} from today.")
                continue

            email_ids = raw_bytes.split()
            print(f"🔍 Found {len(email_ids)} total items inside {folder} from today.\n")

            # --- PROCESS ONLY THE FIRST EMAIL FOUND ---
            email_processed_in_this_run = False
            for e_id in email_ids:
                if email_processed_in_this_run:
                    print("   ℹ️  Stopping after processing one email in this run.")
                    break # Exit the email loop after one iteration

                print(f"--- Processing Email ID: {e_id.decode()} ---")
                try:
                    status, msg_data = mail.fetch(e_id, "(RFC822)")
                    if status != "OK":
                        print(f"   ⚠️ Fetch failed for ID {e_id.decode()}")
                        continue
                    
                    msg_content = None
                    if msg_data and isinstance(msg_data, list):
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg_content = response_part[1]
                                break
                            elif isinstance(response_part, bytes):
                                msg_content = response_part
                                break
                    
                    if msg_content is None:
                        print(f"   ⚠️ No content retrieved for ID {e_id.decode()}")
                        continue
                    
                    try:
                        msg = email.message_from_bytes(msg_content)
                    except Exception as parse_error:
                        print(f"   ⚠️ Error parsing message for ID {e_id.decode()}: {parse_error}")
                        continue
                    
                    msg_id = msg.get("Message-ID", "")
                    if msg_id:
                        msg_id = msg_id.strip("< >")
                    else:
                        msg_id = f"generated-id-{e_id.decode()}"
                    
                    # Check if this specific email ID has already been processed
                    if msg_id in ai_read_memory:
                        print(f"   💾 Skipping {msg_id}, already processed.")
                        continue
                    else:
                        print(f"   🆕 First time seeing ID: {msg_id}")

                    from_header = msg.get("From", "Unknown Sender")
                    raw_date = msg.get("Date", "")
                    
                    try:
                        # 1. Parse the raw date string from the email header
                        parsed_date = email.utils.parsedate_to_datetime(raw_date)
                        
                        # 2. Convert it to Indian Standard Time (IST)
                        ist_date = parsed_date.astimezone(user_tz)
                        
                        # 3. Format it to show only the time (or include date if you prefer)
                        formatted_time = ist_date.strftime("%H:%M:%S") 
                        
                    except Exception:
                        formatted_time = "Unknown Time"

                    # --- FIX FOR SUBJECT DECODING ---
                    raw_subject = msg.get("Subject", "No Subject")
                    decoded_parts = decode_header(raw_subject)
                    
                    if decoded_parts:
                        part, encoding = decoded_parts[0]
                        if isinstance(part, bytes):
                            subject = part.decode(encoding or 'utf-8', errors='ignore')
                        else:
                            subject = part
                    else:
                        subject = "No Subject"
                    # --- END FIX ---

                    print(f"   📥 [{formatted_time} IST] Processing Single Mail:")                    
                    print(f"      From: {from_header}")
                    print(f"      Subject: {subject}")
                    
                    body_text = get_email_body(msg)
                    if not body_text:
                        print("      ⚠️ Skipping processing: No readable text body found.\n")
                        # Even if there's no body, we consider it 'processed' to avoid re-scanning
                        save_to_ai_memory(msg_id)
                        ai_read_memory.add(msg_id) # Update local memory set
                        processed_count += 1
                        print(f"      💾 Marked as Read in AI Memory (no body): {msg_id}\n")
                        print("=" * 80 + "\n")
                        email_processed_in_this_run = True # Mark that an email was handled
                        continue # Move to the next email in the loop, but then break the loop

                    # --- EXTRACT EMAILS FROM THE BODY ---
                    extracted_emails = extract_emails_from_text(body_text)
                    print(f"      Emails found in body: {extracted_emails}") # Print the found emails

                    print("      🖼️ Transforming text fields into secure image matrix canvas...")
                    img_bytes = text_to_image_bytes(from_header, subject, body_text)
                    
                    print("      🧠 Passing image matrix directly to Qwen2.5-VL...")
                    ai_analysis = analyze_image_with_qwen(img_bytes)
                    
                    print(f"\n      🤖 AI Analysis Result:\n{ai_analysis}\n")
                    
                    # --- REVISED GMAIL URL CONSTRUCTION ---
                    # Properly quote the message ID within the search query
                    quoted_msg_id = urllib.parse.quote(f'"{msg_id}"', safe='') # Quote the whole "quoted string"
                    gmail_url = f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{quoted_msg_id}" 
                    print(f"      🔗 Generated Gmail URL for email ID {msg_id}: {gmail_url}")
                    
                    priority = "high" if "Suspension" in ai_analysis or "Winner" in ai_analysis else "default"
                    
                    # Include extracted emails in the alert if any were found
                    alert_body = ai_analysis
                    if extracted_emails:
                         alert_body += f"\n\n📧 Emails found in body: {', '.join(extracted_emails)}"

                    # Attempt to send the ntfy alert - wrap the *call* in a broad try-except
                    try:
                        send_ntfy_alert(alert_body, gmail_url, priority) # Send the modified alert
                        print("      ✅ Analysis dispatched via ntfy successfully.")
                    except Exception as ntfy_error: # Catch any error during the ntfy call
                        print(f"      ❌ Ntfy dispatch failed for {msg_id} (any error): {ntfy_error}")
                        # Decide whether to save the ID if ntfy fails. For now, let's save it anyway,
                        # assuming the core processing (analysis) was attempted.
                        pass # Error already printed, continue with saving.

                    # --- CRITICAL: Save the ID AFTER attempting processing ---
                    save_to_ai_memory(msg_id)
                    ai_read_memory.add(msg_id) # Update local memory set
                    processed_count += 1
                    print(f"      💾 Marked as Read in AI Memory: {msg_id}\n")
                    print("=" * 80 + "\n")
                    email_processed_in_this_run = True # Mark that an email was handled
                    
                except Exception as single_mail_error:
                    print(f"      ⚠️ Unexpected error while processing email ID {e_id.decode()}: {str(single_mail_error)}\n")
                    import traceback
                    traceback.print_exc()
                    continue # Continue to the next email in the loop, but then break the loop
        
        except Exception as folder_error:
            print(f"⚠️ Error processing folder {folder}: {str(folder_error)}\n")
            import traceback
            traceback.print_exc()
            continue # Continue to the next folder in the loop

    mail.logout()
    print("=" * 80)
    print(f"✅ IMAP connection closed.")
    print(f"📊 Processed {processed_count} email(s) in this run.")
    print(f"📂 Total processed emails in memory file ({MEMORY_FILE}): {len(load_ai_memory())}") # Reload to confirm final count


def send_ntfy_alert(ai_analysis, email_url, priority):
    # --- Execution (Following the example pattern closely) ---
    url = f"https://ntfy.sh/{NTFY_TOPIC_NAME.strip('/')}" # Construct the URL correctly using the topic name

    # Clean headers containing only standard text characters
    # Derive priority from input, ensure it's safe
    safe_priority = priority if priority in ['low', 'default', 'high', 'urgent'] else 'default'
    headers = {
        "Title": "👁️ Qwen Vision Secretary Brief", # Safe static title
        "Priority": safe_priority,
        "Click": email_url # This header allows ntfy apps to open a URL on tap
    }

    # Emojis are generally okay in the message body text
    message_body = f"{ai_analysis}\n\n👉 Tap this notification to open email in Gmail."

    # --- Tier 1: Attempt with original data ---
    try:
        response = requests.post(url, data=message_body.encode('utf-8'), headers=headers, timeout=20)
        if response.status_code == 200:
            print(f"   📬 Sent ntfy alert for topic '{NTFY_TOPIC_NAME}' successfully (Tier 1).")
            return # Success, exit the function
        else:
            print(f"   ❌ Ntfy request (Tier 1) failed with status {response.status_code}: {response.text}")
            # Proceed to Tier 2 if status code is not 200
    except Exception as e1:
        print(f"   ❌ Ntfy request (Tier 1) failed due to an exception: {e1}")
        # Proceed to Tier 2 if the request raises an exception (like encoding error)

    # --- Tier 2: Sanitize and retry ---
    print("   Attempting fallback (Tier 2) with sanitized data...")
    # Sanitize the message body and headers by normalizing and removing non-ASCII chars
    try:
        # Normalize the text (NFKD decomposes characters)
        normalized_body = unicodedata.normalize('NFKD', message_body)
        normalized_title = unicodedata.normalize('NFKD', headers["Title"])
        # Encode to ASCII, ignoring characters that can't be encoded
        ascii_body = normalized_body.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
        ascii_title = normalized_title.encode('ascii', errors='ignore').decode('ascii', errors='ignore')

        # Create fallback headers and message
        # IMPORTANT: Ensure no leading/trailing whitespace in sanitized header values
        fallback_headers = {
            "Title": ascii_title.strip(), # Strip whitespace
            "Priority": safe_priority,
            "Click": email_url # Use the original URL, which should be fine
        }
        fallback_message = f"ALERT BODY SANITIZED DUE TO ENCODING ISSUES.\n\n{ascii_body}"

        # Retry the request with sanitized data
        response_fallback = requests.post(url, data=fallback_message.encode('utf-8'), headers=fallback_headers, timeout=20)
        if response_fallback.status_code == 200:
            print(f"   📬 Sent ntfy alert for topic '{NTFY_TOPIC_NAME}' successfully (Tier 2 - Fallback).")
            return # Success with fallback, exit the function
        else:
            print(f"   ❌ Ntfy request (Tier 2 - Fallback) failed with status {response_fallback.status_code}: {response_fallback.text}")
    except Exception as e2:
        print(f"   ❌ Ntfy request (Tier 2 - Fallback) failed due to an exception: {e2}")

    # --- Tier 3: Ultimate Fallback ---
    print("   Attempting ultimate fallback (Tier 3) with basic message...")
    # If both Tiers 1 and 2 fail, send a very basic message
    ultimate_fallback_message = "Email processing completed, but AI analysis could not be sent via ntfy due to encoding/network issues."
    ultimate_fallback_headers = {
        "Title": "Email Processing Alert - Fallback",
        "Priority": "default",
        "Click": email_url
    }
    try:
        response_ultimate = requests.post(url, data=ultimate_fallback_message.encode('utf-8'), headers=ultimate_fallback_headers, timeout=20)
        if response_ultimate.status_code == 200:
             print(f"   📬 Sent basic ntfy alert for topic '{NTFY_TOPIC_NAME}' successfully (Tier 3 - Ultimate Fallback).")
        else:
             print(f"   ❌ Ultimate fallback ntfy request failed with status {response_ultimate.status_code}: {response_ultimate.text}")
    except Exception as e3:
        print(f"   ❌ Ultimate fallback ntfy request failed due to an exception: {e3}")

    # If all tiers fail, raise an error to be caught by the caller's exception handler
    raise RuntimeError("All ntfy sending tiers failed.")


if __name__ == "__main__":
    check_email()
