# import os
# import smtplib
# import time
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# # Pulling credentials safely from GitHub Secrets environment
# SMTP_SERVER = os.environ.get("SMTP_SERVER")
# SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
# EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
# EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# TXT_FILE = "emails.txt"
# EMAIL_SUBJECT = "Message from Awram"
# EMAIL_BODY = "Hello,\n\nThis is a completely automated email sent seamlessly using Python and GitHub Actions!"


# def send_emails():
#     if not all([SMTP_SERVER, EMAIL_USERNAME, EMAIL_PASSWORD]):
#         print("🚨 Error: Missing configuration secrets. Check your GitHub settings.")
#         return

#     if not os.path.exists(TXT_FILE):
#         print(f"🚨 Error: Target file '{TXT_FILE}' was not found.")
#         return

#     try:
#         print("Connecting to secure Gmail SMTP server...")
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()  # Upgrade connection to secure TLS encryption
#         server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
#         print("✅ Authentication successful.")

#         # Read target recipients line by line
#         with open(TXT_FILE, "r", encoding="utf-8") as file:
#             emails = [line.strip() for line in file if line.strip()]

#         print(f"Found {len(emails)} target addresses. Starting delivery...")

#         for index, target_email in enumerate(emails, start=1):
#             print(f"[{index}/{len(emails)}] Sending to: {target_email}")

#             # Assemble email data packet
#             msg = MIMEMultipart()
#             msg["From"] = EMAIL_USERNAME
#             msg["To"] = target_email
#             msg["Subject"] = EMAIL_SUBJECT
#             msg.attach(MIMEText(EMAIL_BODY, "plain"))

#             # Dispatch mail
#             server.send_message(msg)
#             print(f"   ↳ Sent successfully.")

#             # Safe delays (3 seconds) protect your Gmail account reputation from spam flags
#             time.sleep(3)

#         print("\n🎉 Bulk mailing list completed successfully!")

#     except Exception as e:
#         print(f"🚨 A system exception occurred: {e}")
#     finally:
#         try:
#             server.quit()
#             print("Server session closed cleanly.")
#         except NameError:
#             pass  # Session never opened


# if __name__ == "__main__":
#     send_emails()











# import os
# import smtplib
# import time
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# # Correct Gmail SMTP server configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587

# # Sensitive credentials securely coming from GitHub Secrets
# EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
# EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# TXT_FILE = "emails.txt"
# EMAIL_SUBJECT = "Automated Message from GitHub Actions"
# EMAIL_BODY = "Hello,\n\nThis is a completely automated email sent seamlessly using Python and GitHub Actions!"


# def send_emails():
#     # 1. Validate environment variables
#     if not all([EMAIL_USERNAME, EMAIL_PASSWORD]):
#         print("🚨 Error: Missing configuration secrets (EMAIL_USERNAME or EMAIL_PASSWORD). Check your GitHub settings.")
#         return

#     # 2. Validate and read the target file BEFORE opening network connections
#     if not os.path.exists(TXT_FILE):
#         print(f"🚨 Error: Target file '{TXT_FILE}' was not found.")
#         return

#     with open(TXT_FILE, "r", encoding="utf-8") as file:
#         emails = [line.strip() for line in file if line.strip()]

#     if not emails:
#         print("🚨 Error: No valid email addresses found in the target file.")
#         return

#     print(f"Found {len(emails)} target addresses. Starting delivery...")

#     server = None
#     try:
#         # 3. Establish secure connection
#         print(f"Connecting to secure Gmail SMTP server ({SMTP_SERVER}:{SMTP_PORT})...")
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
#         server.starttls()  # Upgrade connection to secure TLS encryption
#         server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
#         print("✅ Authentication successful.")

#         # 4. Send emails
#         for index, target_email in enumerate(emails, start=1):
#             print(f"[{index}/{len(emails)}] Sending to: {target_email}")

#             # Assemble email data packet
#             msg = MIMEMultipart()
#             msg["From"] = EMAIL_USERNAME
#             msg["To"] = target_email
#             msg["Subject"] = EMAIL_SUBJECT
#             msg.attach(MIMEText(EMAIL_BODY, "plain"))

#             # Dispatch mail
#             server.send_message(msg)
#             print("   ↳ Sent successfully.")

#             # Safe delays (3 seconds) protect your Gmail account reputation from spam flags
#             time.sleep(3)

#         print("\n🎉 Bulk mailing list completed successfully!")

#     except smtplib.SMTPAuthenticationError:
#         print("🚨 Authentication failed. Ensure EMAIL_PASSWORD is a valid Gmail 'App Password' (16 characters), not your regular Google account password.")
#     except Exception as e:
#         print(f"🚨 A system exception occurred: {e}")
#     finally:
#         # 5. Safely close the connection
#         if server is not None:
#             try:
#                 server.quit()
#                 print("Server session closed cleanly.")
#             except Exception as e:
#                 print(f"⚠️ Warning: Could not close server session cleanly: {e}")


# if __name__ == "__main__":
#     send_emails()







import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid  # Added for proper Message-ID generation

# Correct Gmail SMTP server configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Sensitive credentials securely coming from GitHub Secrets
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

TXT_FILE = "emails.txt"

# IMPROVED: More natural, less "bot-like" subject and body
EMAIL_SUBJECT = "Update regarding your recent inquiry"  # Change to something relevant to your actual use case
EMAIL_BODY = """Hello,

I hope this message finds you well. 

This is a follow-up regarding our recent communication. Please let me know if you need any further information or assistance.

Best regards,
Your Name / Organization
"""

# IMPROVED: Friendly sender format
SENDER_NAME = "Your Name or Company"  # Replace with your actual name


def send_emails():
    if not all([EMAIL_USERNAME, EMAIL_PASSWORD]):
        print("🚨 Error: Missing configuration secrets (EMAIL_USERNAME or EMAIL_PASSWORD).")
        return

    if not os.path.exists(TXT_FILE):
        print(f"🚨 Error: Target file '{TXT_FILE}' was not found.")
        return

    with open(TXT_FILE, "r", encoding="utf-8") as file:
        emails = [line.strip() for line in file if line.strip()]

    if not emails:
        print("🚨 Error: No valid email addresses found in the target file.")
        return

    print(f"Found {len(emails)} target addresses. Starting delivery...")

    server = None
    try:
        print(f"Connecting to secure Gmail SMTP server ({SMTP_SERVER}:{SMTP_PORT})...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("✅ Authentication successful.")

        for index, target_email in enumerate(emails, start=1):
            print(f"[{index}/{len(emails)}] Sending to: {target_email}")

            msg = MIMEMultipart()
            # IMPROVED: Properly formatted From header
            msg["From"] = f'"{SENDER_NAME}" <{EMAIL_USERNAME}>'
            msg["To"] = target_email
            msg["Subject"] = EMAIL_SUBJECT
            msg["Reply-To"] = EMAIL_USERNAME
            
            # IMPROVED: Add a unique Message-ID (spam filters look for this)
            msg["Message-ID"] = make_msgid(domain=SMTP_SERVER)
            
            msg.attach(MIMEText(EMAIL_BODY, "plain"))

            server.send_message(msg)
            print("   ↳ Sent successfully.")

            # IMPROVED: Increased delay to 5 seconds to mimic human behavior and avoid rate-limiting
            time.sleep(5)

        print("\n🎉 Mailing list completed successfully!")

    except smtplib.SMTPAuthenticationError:
        print("🚨 Authentication failed. Ensure EMAIL_PASSWORD is a valid Gmail 'App Password'.")
    except Exception as e:
        print(f"🚨 A system exception occurred: {e}")
    finally:
        if server is not None:
            try:
                server.quit()
                print("Server session closed cleanly.")
            except Exception as e:
                print(f"⚠️ Warning: Could not close server session cleanly: {e}")


if __name__ == "__main__":
    send_emails()
