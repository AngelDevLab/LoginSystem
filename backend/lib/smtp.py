from fastapi.exceptions import HTTPException
from smtplib import SMTP_SSL
from email.mime.text import MIMEText

from config import settings

def send_gmail(to, subject, message):
    try:
        msg = MIMEText(message, "html")
        msg['Subject'] = subject
        msg['From'] = f'Stock Viewer <{settings.smtp_gmail}>'
        msg['To'] = to
        port = 465  # For SSL

        # Connect to the email server
        server = SMTP_SSL("smtp.gmail.com", port)
        server.login(settings.smtp_gmail, settings.smtp_gmail_password)

        # Send the email
        server.send_message(msg)
        server.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    