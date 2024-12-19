#!/usr/bin/env bash

set -e

docker_compose() {
    docker compose -f compose.tests.yaml "$@"
}

start_services() {
    docker_compose_args=(up -d --remove-orphans)

    if [[ "$PULL_POLICY" ]]; then
        docker_compose_args+=(--pull "$PULL_POLICY")
    fi

    if [[ ! "$SKIP_BUILD" ]]; then
        docker_compose_args+=(--build)
    fi

    docker_compose "${docker_compose_args[@]}"
}

run_tests() {
    docker_compose exec tests /opt/app/commands/pytest.sh
}

main() {
    start_services
    run_tests
}

main
