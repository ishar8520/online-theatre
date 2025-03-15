#!/usr/bin/env bash

set -e

BASE_DIR=/opt/app
SOURCE_PATHS=("$BASE_DIR/notifications_queue")

main() {
    mypy "${SOURCE_PATHS[@]}"
}

main "$@"
