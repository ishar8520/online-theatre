import logging
from time import sleep

from src.core.config import settings
from src.services.clickhouse import ClickhouseService
from src.services.data_transformer import TransformerFactory
from src.services.exceptions import (
    InvalidTransformData,
    UnknownTransformerType,
)
from src.services.kafka_consumer import KafkaConsumerService


def main() -> None:
    kafka_service = KafkaConsumerService()
    clickhouse_client = ClickhouseService(
        batch_size=settings.clickhouse.batch_size,
        flush_interval=settings.clickhouse.flush_interval
    )

    while True:
        clickhouse_client.check_auto_flush()

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
                    transformed_data = transformer.transform()
                    table_name = transformer.get_type()

                    clickhouse_client.add_to_batch(table_name, transformed_data)
                    if clickhouse_client.is_batch_full(table_name):
                        clickhouse_client.flush_table(table_name)
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
