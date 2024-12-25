#!/usr/bin/env bash

set -e

docker_compose() {
    docker compose -f compose.tests.yaml "$@"
}

docker_compose_up() {
    docker_compose up --remove-orphans "$@"
}

start_services() {
    local docker_compose_args=(-d)

    if [[ "$PULL_POLICY" ]]; then
        docker_compose_args+=(--pull "$PULL_POLICY")
    fi

    if [[ ! "$SKIP_BUILD" ]]; then
        docker_compose_args+=(--build)
    fi

    docker_compose_up "${docker_compose_args[@]}"
}

watch_services() {
    docker_compose_up --watch --pull always --build --force-recreate
}

run_tests() {
    docker_compose exec tests /opt/app/commands/pytest.sh
}

main() {
    local command="$1"

    case "$command" in
        watch) watch_services; exit ;;
        tests) run_tests; exit ;;
    esac

    start_services
    run_tests
}

main "$@"
