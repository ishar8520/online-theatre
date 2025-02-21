from core.utils import handle_kafka_errors
from models.event import ClickEvent, CustomEvent, EventContainer, PageViewEvent
from quart import Quart, jsonify, request
from quart_schema import QuartSchema

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
@handle_kafka_errors
async def track_click():
    return await process_event(ClickEvent, "click")


@app.route("/track_page_view", methods=["POST"])
@handle_kafka_errors
async def track_page_view():
    return await process_event(PageViewEvent, "page_view")


@app.route("/track_custom_event", methods=["POST"])
@handle_kafka_errors
async def track_custom_event():
    return await process_event(CustomEvent, "custom_event")
