import asyncio
from aio_pika import connect, Message
from pydantic import BaseModel

class RabbitConfig(BaseModel):
    username: str = 'username'
    password: str = 'password'
    host: str = 'localhost'
    port: int = 5672
    
    @property
    def url(self) -> str:
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'

async def send_message_to_queue(message: str):
    rabbitmq = RabbitConfig()
    connection = await connect(rabbitmq.url)
    channel = await connection.channel()
    
    queue = await channel.declare_queue('undelivered_messages', passive=True)
    
    await channel.default_exchange.publish(
        Message(
            body=message.encode(),
        ),
        routing_key=queue.name,
    )
    
    print(f'Сообщение отправлено: {message}')
    await connection.close()

if __name__ == '__main__':
    while True:
        message = input('Введите сообщение для отправки: ')
        asyncio.run(send_message_to_queue(message))