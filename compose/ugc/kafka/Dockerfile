FROM bitnami/kafka:3.4

# Переходим на root для изменения прав доступа
USER root

# Копируем скрипт в контейнер
COPY init-kafka.sh /opt/bitnami/scripts/init-kafka.sh

# Делаем скрипт исполнимым
RUN chmod +x /opt/bitnami/scripts/init-kafka.sh