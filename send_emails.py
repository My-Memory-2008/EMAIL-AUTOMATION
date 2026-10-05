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












import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Hardcoded public Gmail configurations to bypass DNS/Secret lookup errors
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587

# Keep sensitive credentials securely coming from GitHub Secrets
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

TXT_FILE = "emails.txt"
EMAIL_SUBJECT = "Automated Message from GitHub Actions"
EMAIL_BODY = "Hello,\n\nThis is a completely automated email sent seamlessly using Python and GitHub Actions!"


def send_emails():
    if not all([EMAIL_USERNAME, EMAIL_PASSWORD]):
        print("🚨 Error: Missing configuration secrets (EMAIL_USERNAME or EMAIL_PASSWORD). Check your GitHub settings.")
        return

    if not os.path.exists(TXT_FILE):
        print(f"🚨 Error: Target file '{TXT_FILE}' was not found.")
        return

    try:
        print(f"Connecting directly to secure Gmail SMTP server ({SMTP_SERVER}:{SMTP_PORT})...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()  # Upgrade connection to secure TLS encryption
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("✅ Authentication successful.")

        # Read target recipients line by line
        with open(TXT_FILE, "r", encoding="utf-8") as file:
            emails = [line.strip() for line in file if line.strip()]

        print(f"Found {len(emails)} target addresses. Starting delivery...")

        for index, target_email in enumerate(emails, start=1):
            print(f"[{index}/{len(emails)}] Sending to: {target_email}")

            # Assemble email data packet
            msg = MIMEMultipart()
            msg["From"] = EMAIL_USERNAME
            msg["To"] = target_email
            msg["Subject"] = EMAIL_SUBJECT
            msg.attach(MIMEText(EMAIL_BODY, "plain"))

            # Dispatch mail
            server.send_message(msg)
            print(f"   ↳ Sent successfully.")

            # Safe delays (3 seconds) protect your Gmail account reputation from spam flags
            time.sleep(3)

        print("\n🎉 Bulk mailing list completed successfully!")

    except Exception as e:
        print(f"🚨 A system exception occurred: {e}")
    finally:
        try:
            server.quit()
            print("Server session closed cleanly.")
        except NameError:
            pass  # Session never opened


if __name__ == "__main__":
    send_emails()
