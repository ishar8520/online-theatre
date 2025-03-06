from __future__ import annotations

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from quart import Quart
from .api.v1.endpoints.bookmark import bookmark_blueprint
from .core.settings import settings
from .models.mongo import Bookmark

app = Quart(__name__)

app.config['QUART_SCHEMA_CONVERT_CASING'] = False
app.config['QUART_SCHEMA_CONVERSION_PREFERENCE'] = 'camel_case'


@app.before_serving
async def configure():
    client = AsyncIOMotorClient(f'mongodb://{settings.mongo.host}:{settings.mongo.port}')
    await init_beanie(
        client.get_database(settings.mongo.db),
        document_models=[Bookmark]
    )

app.register_blueprint(bookmark_blueprint, url_prefix='/v1/bookmark')
