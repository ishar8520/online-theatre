import asyncio
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
import logging
from resender.config import settings

logging.basicConfig(level=logging.INFO)

async def process_message(message: AbstractIncomingMessage) -> None:
    try:
        logging.info(f'Обработано: {message.body.decode()}')
        await message.ack()
    except Exception as error:
        logging.error(f'Ошибка: {error}')
        await message.nack(requeue=False)

async def check_queue():
    try:
        connection = await connect(settings.rabbitmq.url)
        channel = await connection.channel()
        queue = await channel.declare_queue('undelivered_messages', passive=True)
        
        processed_count = 0
        while True:
            message = await queue.get(fail=False)
            if not message:
                break
            await process_message(message)
            processed_count += 1
        
        logging.info(f'Обработано сообщений: {processed_count}')
        await connection.close()
        return processed_count
        
    except Exception as error:
        logging.error(f'Ошибка подключения: {error}')
        return 0

async def main_loop():
    while True:
        processed = await check_queue()
        if processed == 0:
            logging.info('Очередь пуста. Ожидание 5 минут...')
        await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main_loop())
