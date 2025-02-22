from core.utils import handle_kafka_errors
from models.event import ClickEvent, CustomEvent, EventContainer, PageViewEvent
from quart import Quart, jsonify, request
from quart_schema import QuartSchema, validate_request

from .event import get_kafka_event_repo

app = Quart(__name__)
QuartSchema(app)

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


async def process_event(event_class, event_type):
    data = await request.get_json()
    event = event_class(**data)
    event_container = EventContainer(model=event)
    await kafka_producer.send_event(event_container)
    return jsonify(
        {"status": "success", "event": event_type, "data": event.model_dump()}
    )

@app.route("/track_click", methods=["POST"])
@validate_request(ClickEvent)
@handle_kafka_errors
async def track_click(data):
    return await process_event(ClickEvent, "click")


@app.route("/track_page_view", methods=["POST"])
@validate_request(PageViewEvent)
@handle_kafka_errors
async def track_page_view(data):
    return await process_event(PageViewEvent, "page_view")


@app.route("/track_custom_event", methods=["POST"])
@validate_request(CustomEvent)
@handle_kafka_errors
async def track_custom_event(data):
    return await process_event(CustomEvent, "custom_event")
