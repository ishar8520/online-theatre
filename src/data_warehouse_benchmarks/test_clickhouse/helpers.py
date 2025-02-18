import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Generator

import faker


def format_time(seconds):
    """
    Возвращает время в двух форматах:
    - Научная нотация (например, 8.98e-05)
    - Человекочитаемый формат (например, 89.80 мкс)
    """
    if seconds >= 60:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        human_readable = f"{minutes} мин {remaining_seconds:.2f} сек"
    elif seconds >= 1:
        human_readable = f"{seconds:.2f} сек"
    elif seconds >= 1e-3:
        human_readable = f"{seconds * 1e3:.2f} мс"
    elif seconds >= 1e-6:
        human_readable = f"{seconds * 1e6:.2f} мкс"
    else:
        human_readable = f"{seconds * 1e9:.2f} нс"

    return f"{seconds:.2e} секунд ({human_readable})"


def measure_time(operation_name):
    """
    Декоратор, измеряющий время выполнения функции.
    :param operation_name: Название операции (например, "Вставка", "Чтение", "Обновление").
    """
    def inner_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            total_records = kwargs.get("total")
            speed_time = execution_time / total_records

            formatted_execution_time = format_time(execution_time)
            formatted_speed_time = format_time(speed_time)

            print(f"{operation_name} {total_records} записей: {formatted_execution_time}")
            print(f"Средняя скорость обработки одной записи: {formatted_speed_time}")

            return result

        return wrapper

    return inner_decorator


fake = faker.Faker()


def generate_test_event() -> dict:
    """Генерирует одну тестовую запись (event) для БД."""

    now = datetime.now()

    return {
        "type": "click",
        "timestamp": (now - timedelta(hours=random.randint(1, 3))).isoformat(),
        "user_id": str(uuid.uuid4()),
        "fingerprint": fake.user_agent(),
        "element": random.choice(["film", "video", "article", "image"]),
        "url": f'http://{random.choice(["smth", "yandex", "vk"])}.ru',
    }


def generate_batched_events(count: int, batch_size: int) -> Generator[list[dict], None, None]:
    """Генерирует заданное количество записей и возвращает их указанными батчами."""

    def event_generator() -> Generator[list[dict], None, None]:
        batch = []
        for i in range(count):
            batch.append(generate_test_event())
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    return event_generator()
