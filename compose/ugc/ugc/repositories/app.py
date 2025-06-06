import sentry_sdk
from core.config import sentry_settings
from core.utils import handle_kafka_errors
from models.event import ClickEvent, CustomEvent, EventContainer, PageViewEvent
from quart import Quart, jsonify, request
from quart_schema import QuartSchema, validate_request

from .event import get_kafka_event_repo

if sentry_settings.enable_sdk:

    sentry_sdk.init(
        dsn=sentry_settings.dsn,
        traces_sample_rate=sentry_settings.traces_sample_rate,
        profiles_sample_rate=sentry_settings.profiles_sample_rate,
        enable_tracing=sentry_settings.enable_tracing,
    )
    sentry_sdk.set_tag("service_name", "ugc-service")

app = Quart(__name__)
QuartSchema(
    app,
    openapi_path="/ugc/openapi.json",
    servers=[{"url": "/ugc", "description": "Base URL for UGC Service"}],
)

kafka_producer = None


@app.before_serving
async def startup():
    global kafka_producer
    kafka_producer = get_kafka_event_repo()
    await kafka_producer.start()


@app.after_serving
async def shutdown():
    if kafka_producer:
        await kafka_producer.stop()


async def send_event_async(event_container):
    await kafka_producer.send_event(event_container)


async def process_event(event_class, event_type, topic):
    data = await request.get_json()
    event = event_class(**data)
    event_container = EventContainer(model=event)
    await kafka_producer.send_event(event_container, topic)
    return jsonify(
        {"status": "success", "event": event_type, "data": event.model_dump()}
    )


@app.route("/track_click", methods=["POST"])
@validate_request(ClickEvent)
@handle_kafka_errors
async def track_click(data):
    event_type = topic = 'click'
    return await process_event(ClickEvent, event_type, topic)


@app.route("/track_page_view", methods=["POST"])
@validate_request(PageViewEvent)
@handle_kafka_errors
async def track_page_view(data):
    event_type = topic = 'page_view'
    return await process_event(PageViewEvent, event_type, topic)


@app.route("/track_custom_event", methods=["POST"])
@validate_request(CustomEvent)
@handle_kafka_errors
async def track_custom_event(data):
    event_type = topic = 'custom_event'
    return await process_event(CustomEvent, event_type, topic)
