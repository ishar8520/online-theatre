#!/bin/sh

# Ждем, пока Kafka станет доступна
echo "Waiting for Kafka to be ready..."
until kafka-topics.sh --bootstrap-server kafka-0:9092 --list; do
  sleep 1
done

# Получаем имя топика из переменной окружения
echo "Creating Kafka topic: ${KAFKA_TOPIC}"
kafka-topics.sh --bootstrap-server kafka-0:9092 --create --if-not-exists --topic ${KAFKA_TOPIC} --partitions 1

# Выводим список топиков
echo "Successfully created the following topics:"
kafka-topics.sh --bootstrap-server kafka-0:9092 --list