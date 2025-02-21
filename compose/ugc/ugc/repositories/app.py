import json
from flask import Flask, jsonify, request
from event import get_kafka_event_repo
from models.event import ClickEvent, EventContainer, PageViewEvent, CustomEvent
import asyncio

app = Flask(__name__)

kafka_producer = None
loop = asyncio.new_event_loop()


async def start_kafka_producer():
    global kafka_producer
    kafka_producer = get_kafka_event_repo()
    await kafka_producer.start()


async def stop_kafka_producer():
    if kafka_producer:
        await kafka_producer.stop()


@app.before_request
def before_first_request():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_kafka_producer())


@app.teardown_appcontext
def teardown_appcontext(exception=None):
    loop.run_until_complete(stop_kafka_producer())


async def send_event_async(event_container):
    await kafka_producer.send_event(event_container)


@app.route("/track_click", methods=["POST"])
def track_click():
    data = request.json
    click_event = ClickEvent(**data)
    event_container = EventContainer(model=click_event)
    loop.run_until_complete(send_event_async(event_container))
    return jsonify(
        {"status": "success", "event": "click", "data": click_event.model_dump()}
    )


@app.route("/track_page_view", methods=["POST"])
def track_page_view():
    data = request.json
    page_view_event = PageViewEvent(**data)
    event_container = EventContainer(model=page_view_event)
    loop.run_until_complete(send_event_async(event_container))
    return jsonify(
        {
            "status": "success",
            "event": "page_view",
            "data": page_view_event.model_dump(),
        }
    )


@app.route("/track_custom_event", methods=["POST"])
def track_custom_event():
    data = request.json
    custom_event = CustomEvent(**data)
    event_container = EventContainer(model=custom_event)
    loop.run_until_complete(send_event_async(event_container))
    return jsonify(
        {
            "status": "success",
            "event": "custom_event",
            "data": custom_event.model_dump(),
        }
    )


if __name__ == "__main__":
    app.run(port=5001, host="0.0.0.0", debug=True)
