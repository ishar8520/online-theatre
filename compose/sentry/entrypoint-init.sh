#!/bin/bash
set -e

echo "Запускаем миграции Sentry..."
sentry upgrade --noinput

echo "Создаем администратора (если еще не создан)..."
sentry shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$SENTRY_ADMIN_EMAIL').exists():
    User.objects.create_superuser(username='$SENTRY_ADMIN_EMAIL', email='$SENTRY_ADMIN_EMAIL', password='$SENTRY_ADMIN_PASSWORD')
EOF

echo "Инициализация завершена."
