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

### Запуск тестов с использованием Docker Compose Watch

В одном окне терминала стартуем сервисы в watch mode:

```shell
$ ./run_tests.sh watch
```

Когда все контейнеры с сервисами запустятся, в другом окне терминала выполняем уже сами тесты:

```shell
$ ./run_tests.sh tests
```
