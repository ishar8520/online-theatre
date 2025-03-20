import string
from random import choice, randint, shuffle

from config import SHORT_LINK_TTL
from redis.asyncio import Redis


class ShortenerService:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def get_unique_short_id() -> str:
        final = ""
        for _ in range(2):
            random_upper = choice(string.ascii_uppercase)
            random_lower = choice(string.ascii_lowercase)
            random_num = randint(0, 9)
            mix = random_upper + random_lower + str(random_num)
            mixed = list(mix)
            shuffle(mixed)
            mixed = "".join(mixed)
            final += mixed
        return final

    async def create_short_url(self, url: str, user_id: str) -> str:
        redis_key = f"{user_id}:{url}"
        existing_short_code = await self.redis.get(redis_key)
        if existing_short_code:
            return existing_short_code
        short_code = self.get_unique_short_id()
        await self.redis.set(redis_key, short_code, ex=SHORT_LINK_TTL)
        await self.redis.set(short_code, url, ex=SHORT_LINK_TTL)
        return short_code

    async def get_original_url(self, short_code: str) -> str:
        url = await self.redis.get(short_code)
        return url
