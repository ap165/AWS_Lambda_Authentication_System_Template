import smtplib
from email.message import EmailMessage
from config import SMTP_FROM_EMAIL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS

def send_email(user, to_email, subject, body, body_type="html"):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{user}@{SMTP_FROM_EMAIL}"
    msg["To"] = to_email

    msg.set_content(body, subtype=body_type)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)
