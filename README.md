# online-theatre

Проект онлайн-кинотеатра.

## Запуск проекта в Docker Compose

* _compose.yaml_ &mdash; запуск основного приложения с данными из _сompose/postgresql/database_dump.sql_.
* _compose.faker.yaml_ &mdash; запуск основного приложения со сгенерированными данными из faker (генерирует
200000 фильмов).

### Запуск в режиме продакшн

```shell
$ ./run_server.sh
```

### Запуск в режиме для разработчиков (с использованием Docker Compose Watch)

```shell
$ ./run_server.sh dev
```

## Запуск тестов в Docker Compose

### Стандартный запуск тестов

```shell
$ ./run_tests.sh
```

### Запуск тестов с указанием версии Python

```shell
$ PYTHON_VERSION=3.12 ./run_tests.sh
```

### Запуск тестов с использованием Docker Compose Watch

В одном окне терминала стартуем сервисы в watch mode:

```shell
$ ./run_tests.sh watch
```

Когда все контейнеры с сервисами запустятся, в другом окне терминала выполняем уже сами тесты:

```shell
$ ./run_tests.sh tests
```

## Статический анализ кода

### Стандартный запуск в Docker Compose

В качестве первого параметра скрипта необходимо передать название вида статического анализа.
Если второй параметр не задан, то соответствующая команда будет запущена в контейнере каждого
поддерживаемого сервиса из Compose file:

```shell
$ ./run_lint.sh mypy
```

Доступны следующие названия команд статического анализа:
* `mypy`

В качестве второго параметра можно указать название конкретного сервиса, код которого необходимо
проанализировать:

```shell
$ ./run_lint.sh mypy movies
```

### Запуск с использованием Docker Compose Watch

В одном окне терминала:

```shell
$ ./run_lint.sh watch
```

В другом окне терминала:

```shell
$ ./run_lint.sh watch mypy
```

Также возможен статический анализ кода конкретного сервиса:

```shell
$ ./run_lint.sh watch mypy movies
```

# Тестирование по выбору хранилища UGC
### Результаты тестирования по выбору хранилища UGC представлены в папке test_database


# Над проектом работали:
## Шаров Илья (ЯП: @i.sh.8520, github: @ishar8520) - тимлид
## Мария Пирогова (ЯП: @miss.yefimenko, github: @Maliarda) - разработчик
## Лашков Максим (ЯП: @maxim.lashkov, github: @maximlashkov) - разработчик
## Максим Павленков (ЯП: @edmpeople0, github: @maks-pavlenkov) - разработчик
