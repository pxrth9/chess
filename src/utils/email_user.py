import smtplib
from email.mime.text import MIMEText
import os
from utils.logger import logger as log


# Environment variables
FROM_EMAIL = os.environ.get("FROM_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")


def send_email(
    subject, body, sender=FROM_EMAIL, recipient=TO_EMAIL, password=APP_PASSWORD
):
    # Validate required fields
    if not (sender and recipient and password):
        log.error("Missing required email configuration.")
        log.error(
            f"Sender: {sender}, Recipient: {recipient}, Password: {'***' if password else None}"
        )
        return False

    try:
        # Create the email message
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        # Send the email using SMTP over SSL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            log.info("Connecting to SMTP server...")
            smtp_server.login(sender, password)
            log.info("Successfully logged in to SMTP server.")
            smtp_server.sendmail(sender, recipient, msg.as_string())
            log.info("Email sent successfully.")
        return True
    except smtplib.SMTPException as smtp_error:
        log.error(f"SMTP error occurred: {smtp_error}")
    except Exception as e:
        log.error(f"An unexpected error occurred while sending email: {e}")
    return False
