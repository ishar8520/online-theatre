from models.event import ClickEvent, CustomEvent, EventContainer, PageViewEvent
from quart import Quart, jsonify, request

from .event import get_kafka_event_repo

app = Quart(__name__)

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


@app.route("/track_click", methods=["POST"])
async def track_click():
    data = await request.get_json()
    click_event = ClickEvent(**data)
    event_container = EventContainer(model=click_event)
    await send_event_async(event_container)
    return jsonify(
        {"status": "success", "event": "click", "data": click_event.model_dump()}
    )


@app.route("/track_page_view", methods=["POST"])
async def track_page_view():
    data = await request.get_json()
    page_view_event = PageViewEvent(**data)
    event_container = EventContainer(model=page_view_event)
    await send_event_async(event_container)
    return jsonify(
        {
            "status": "success",
            "event": "page_view",
            "data": page_view_event.model_dump(),
        }
    )


@app.route("/track_custom_event", methods=["POST"])
async def track_custom_event():
    data = await request.get_json()
    custom_event = CustomEvent(**data)
    event_container = EventContainer(model=custom_event)
    await send_event_async(event_container)
    return jsonify(
        {
            "status": "success",
            "event": "custom_event",
            "data": custom_event.model_dump(),
        }
    )
