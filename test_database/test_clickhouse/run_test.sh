#!/usr/bin/env bash

set -e

docker compose up --build --abort-on-container-exit
docker-compose down
