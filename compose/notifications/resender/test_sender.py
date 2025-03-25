import asyncio
from aio_pika import connect, Message
from pydantic import BaseModel

class RabbitConfig(BaseModel):
    username: str = 'username'
    password: str = 'pass'
    host: str = 'localhost'
    port: int = 5672
    
    @property
    def url(self) -> str:
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'

async def send_message_to_queue(message: str):
    rabbitmq = RabbitConfig()
    """Отправляет сообщение в очередь taskiq.dead_letter"""
    connection = await connect(rabbitmq.url)
    channel = await connection.channel()
    
    # Объявляем очередь (параметры должны совпадать с consumer!)
    queue = await channel.declare_queue('taskiq.dead_letter', durable=False)
    
    # Отправляем сообщение
    await channel.default_exchange.publish(
        Message(
            body=message.encode(),
            delivery_mode=2,  # Сообщение будет сохраняться при перезагрузке RabbitMQ (если очередь durable)
        ),
        routing_key=queue.name,
    )
    
    print(f"Сообщение отправлено: {message}")
    await connection.close()

if __name__ == '__main__':
    message = input("Введите сообщение для отправки: ")
    asyncio.run(send_message_to_queue(message))