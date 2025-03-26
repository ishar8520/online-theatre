from email.message import EmailMessage
from aiosmtplib import SMTP
from queue.notifications_queue.core.config import settings

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.email.from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    
    async with SMTP(
        hostname=settings.smtp.host,
        port=settings.smtp.port,
        username=settings.smtp.username,
        password=settings.smtp.password,
        use_tls=False
    ) as smtp:
        await smtp.send_message(message)
