import json
from time import sleep

from src.services.data_transformer import (
    ClickEventTransformer,
    TransformerFactory
)
from src.services.kafka_topics import KafkaTopicEnum
from src.services.exceptions import (
    InvalidTransformData,
)
from src.services.kafka_consumer import KafkaConsumerService
from src.services.clickhouse import ClickhouseService
import logging


def main() -> None:
    clickhouse_client = ClickhouseService()

    while True:
        need_sleep = True

        for topic in KafkaTopicEnum:
            kafka_service = KafkaConsumerService(topic.value)

            message_pack = kafka_service.poll()
            if not message_pack:
                continue

            try:
                for _, messages in message_pack.items():
                    batch = []
                    for message in messages:
                        data = message.value.decode("utf-8")
                        transformer = TransformerFactory.get(topic.value, data)
                        batch.append(transformer.transform())

                    if batch:
                        clickhouse_client.insert(
                            ClickEventTransformer.get_type(),
                            batch[0].keys(),
                            batch
                        )
                        kafka_service.commit()

                        need_sleep = False
                        logging.info('Success insert!')
            except InvalidTransformData:
                logging.error('Invalid transform data!')
            finally:
                continue

        if need_sleep:
            sleep(0)


if __name__ == '__main__':
    main()
