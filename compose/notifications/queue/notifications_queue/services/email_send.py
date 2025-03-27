import json
import logging
from email.message import EmailMessage
from aiosmtplib import SMTP
from fastapi import HTTPException, status
from aio_pika import Message, DeliveryMode

from notifications_queue.core.config import settings
from notifications_queue.services.rabbitmq import RabbitMQ

logging.basicConfig(level=logging.INFO)


async def send_to_dead_letter_queue(email_data: dict):
    try:
        channel = await RabbitMQ.get_channel()
        queue = await channel.declare_queue(settings.dlq.queue, passive=True)
        
        await channel.default_exchange.publish(
            Message(
                body=json.dumps(email_data).encode(),
                delivery_mode=DeliveryMode.PERSISTENT
            ),
            routing_key=queue.name,
        )
    except Exception as error:
       logging.error(f"Failed to send to dead letter queue: {error}")

async def send_email(to: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.email.from_email
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    async with SMTP(
        hostname=settings.smtp.host,
        port=settings.smtp.port,
        username=settings.smtp.username,
        password=settings.smtp.password,
        use_tls=False
    ) as smtp:
        try:
            await smtp.send_message(message)
            logging.info(f"Message succesfully send to {message['To']}")
        except Exception as error:
            logging.error(f"Message send to {message['To']} with error: {str(error)}")
            await send_to_dead_letter_queue(
                {
                    "to": to,
                    "subject": subject,
                    "body": body
                })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email. Message added to dead letter queue. Error: {str(error)}"
        )
