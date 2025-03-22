#!/usr/bin/env bash

set -e

main() {
    taskiq_args=()

    if [[ "$TASKIQ_WORKERS" ]]; then
        taskiq_args+=(--workers "$TASKIQ_WORKERS")
    fi

    if [[ "$TASKIQ_RELOAD" ]]; then
        taskiq_args+=(--reload)
    fi

    taskiq worker "${taskiq_args[@]}" notifications_queue.broker:broker
}

main "$@"
