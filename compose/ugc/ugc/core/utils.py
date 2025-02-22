from functools import wraps
from http import HTTPStatus

from aiokafka.errors import KafkaConnectionError, KafkaError, KafkaTimeoutError
from quart import jsonify
from repositories.event import logger


def handle_kafka_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KafkaConnectionError as e:
            logger.error(f"Kafka connection error: {e}")
            return (
                jsonify({"status": "error", "message": "Kafka is unavailable"}),
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
        except KafkaTimeoutError as e:
            logger.error(f"Kafka timeout error: {e}")
            return (
                jsonify({"status": "error", "message": "Kafka request timed out"}),
                HTTPStatus.GATEWAY_TIMEOUT,
            )
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            return (
                jsonify({"status": "error", "message": "Kafka error occurred"}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return (
                jsonify({"status": "error", "message": "Internal server error"}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    return wrapper
