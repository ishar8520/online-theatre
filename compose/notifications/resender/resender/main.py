import time
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
import asyncio
import logging

from resender.config import settings

logging.basicConfig(level=logging.INFO)

async def handler(message: AbstractIncomingMessage) -> None:
    try:
        logging.info(f'Получено: {message.body.decode()}')
        await message.ack()
    except Exception:
        await message.nack() 


async def resender_loop():
    while True:
        try:
            connection = await connect(settings.rabbitmq.url, timeout=10)
            logging.info('Подключение к rabbitmq установлено')
            break
        except Exception:
            continue
    channel = await connection.channel()
    queue = await channel.declare_queue('taskiq.dead_letter')
    await queue.consume(handler)
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        
        
if __name__ == '__main__':
    asyncio.run(resender_loop())
