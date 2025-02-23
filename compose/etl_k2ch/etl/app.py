from time import sleep

from src.services.exceptions import (
    InvalidTransformData,
    UnknownTransformerType
)
from src.services.kafka_consumer import KafkaConsumerService
from src.services.clickhouse import ClickhouseService
from src.services.data_transformer import TransformerFactory
import logging


def main() -> None:
    kafka_service = KafkaConsumerService()
    clickhouse_client = ClickhouseService()

    while True:
        message_pack = kafka_service.poll()
        if not message_pack:
            sleep(2)

        for topic, messages in message_pack.items():
            for message in messages:
                data_json = message.value.decode("utf-8")

                try:
                    transformer = TransformerFactory.get(
                        event_name=topic[0],
                        data=data_json
                    )
                    data = transformer.transform()

                    clickhouse_client.insert(transformer.get_type(), data)
                    kafka_service.commit()

                    logging.info('Success insert!')
                except InvalidTransformData:
                    logging.error('Invalid transform data!')
                except UnknownTransformerType:
                    logging.error('Unknown transformer type!')
                finally:
                    continue


if __name__ == '__main__':
    main()
