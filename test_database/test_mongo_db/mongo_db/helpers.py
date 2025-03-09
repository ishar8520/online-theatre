import time


result_measure = []


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
    :param operation_name: Название операции (например, 'Вставка', 'Чтение', 'Обновление').
    """

    def inner_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            formatted_execution_time = format_time(execution_time)

            result_measure.append(f"{operation_name}: {formatted_execution_time}")
            return result

        return wrapper

    return inner_decorator


def output_result():
    return result_measure
