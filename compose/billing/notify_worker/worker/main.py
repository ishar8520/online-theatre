from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage
import asyncio
import httpx
import json
import uuid
import aiohttp
import logging
from config import settings


logging.basicConfig(level=logging.INFO)

async def get_superuser() -> dict:
    async with aiohttp.ClientSession() as session:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-Id': str(uuid.uuid4())
        }
        superuser = {
            'grant_type': 'password',
            'username': settings.auth.login,
            'password': settings.auth.password
        }
        url = f'http://{settings.auth.host}:{settings.auth.port}/auth/api/v1/jwt/login/'
        async with session.post(url, headers=headers, data=superuser) as response:
            data = await response.json()
            token_jwt = data['access_token']
            token_type = data['token_type']
            headers = {
                'accept': 'application/json',
                'Authorization': f'{token_type.title()} {token_jwt}',
                'Content-Type': 'application/json',
                'X-Request-Id': str(uuid.uuid4())
            }
            return headers

class RabbitWorker:
    def __init__(self, rabbitmq_url: str, queue_name: str, api_url: str, max_tasks: int) -> None:
        self.rabbitmq_url = rabbitmq_url
        self.queue_name = queue_name
        self.api_url = api_url
        self.max_tasks = max_tasks
        self.semaphore = asyncio.Semaphore(max_tasks)
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout=5))
        self.connection = None
        self.channel = None
        self.superuser_headers = {}

    async def make_api_request(self, message_data: dict) -> bool:
        try:
            url = f'{self.api_url}/{message_data["label"]}'
            response = await self.client.post(
                url,
                headers=self.superuser_headers,
                json=message_data,
            )
            if response.is_success:
                result = response.json()
                logging.info(f'API response: {result}')
                return True
            logging.error(f'API request failed with status {response.status_code}: {response.text}')
            return False
        except httpx.TimeoutException:
            logging.error('API request timed out')
            return False
        except httpx.RequestError as e:
            logging.error(f'HTTP request error: {str(e)}')
            return False
        except json.JSONDecodeError:
            logging.error(f'Invalid JSON response from API: {response.text}')
            return False
        except Exception as e:
            logging.error(f'Unexpected error making API request: {str(e)}')
            return False

    async def setup_rabbitmq(self) -> None:
        self.connection = await connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.max_tasks)
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,
        )
        
    async def consume(self) -> None:
        await self.queue.consume(self.process_message)

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                async with self.semaphore:
                    message_data = json.loads(message.body.decode())
                    success = await self.make_api_request(message_data)
                    if not success:
                        logging.warning(f'Failed to process message: {message.body.decode()}')
            except json.JSONDecodeError:
                logging.error(f'Invalid JSON message: {message.body.decode()}')
            except Exception as e:
                logging.error(f'Error processing message: {str(e)}')

    async def run(self) -> None:
        logging.info('Starting async worker...')
        await self.setup_rabbitmq()
        await self.consume()
        logging.info('Worker is running. Press CTRL+C to exit.')
        self.superuser_headers = await get_superuser()
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            logging.info('Worker stopped')

    async def stop(self) -> None:
        await self.client.aclose()
        if self.connection:
            await self.connection.close()
        logging.info('Worker shutdown completed')


async def worker() -> None:
    worker = RabbitWorker(
        rabbitmq_url=settings.rabbitmq.url,
        queue_name=settings.rabbitmq.queue_name,
        api_url=f'http://{settings.billing.host}:{settings.billing.port}/billing/api/v1/payment/process',
        max_tasks=10
    )
    try:
        await worker.run()
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == '__main__':
    asyncio.run(worker())
    
    