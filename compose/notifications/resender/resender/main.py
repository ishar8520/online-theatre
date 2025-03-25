import time
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
import asyncio

from resender.config import settings


async def handler(message: AbstractIncomingMessage) -> None:
    try:
        print(f"Получено: {message.body.decode()}")
        await message.ack()
    except Exception:
        await message.nack() 


async def resender_loop():
    connection = await connect(f'amqp://{settings.rabbitmq.username}:{settings.rabbitmq.password}@{settings.rabbitmq.host}:{settings.rabbitmq.port}/')
    channel = await connection.channel()
    queue = await channel.declare_queue('hello_default', durable=True)
    await queue.consume(handler)
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        
        
if __name__ == '__main__':
    asyncio.run(resender_loop)
