#!/usr/bin/env bash

set -e

APP_PATH=/opt/app/notifications_queue/main.py

fastapi_dev() {
    fastapi dev --host 0.0.0.0 "$APP_PATH"
}

fastapi_run() {
    fastapi_args=()

    if [[ "$FASTAPI_WORKERS" ]]; then
        fastapi_args+=(--workers "$FASTAPI_WORKERS")
    fi

    fastapi run "${fastapi_args[@]}" "$APP_PATH"
}

main() {
    local command="$1"

    case "$command" in
        dev) fastapi_dev; exit ;;
        run) fastapi_run; exit ;;
    esac

    fastapi_run
}

main "$@"
