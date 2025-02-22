from time import sleep

from src.services.kafka_consumer import KafkaConsumerService


def main() -> None:
    kafka_service = KafkaConsumerService()

    while True:
        message_pack = kafka_service.poll()
        if not message_pack:
            sleep(20)

        for topic, messages in message_pack.items():
            for message in messages:
                # sent to ClickHouse
                print("key=%s value=%s" % (message.key.decode("utf-8"), message.value.decode("utf-8")))


if __name__ == '__main__':
    main()
