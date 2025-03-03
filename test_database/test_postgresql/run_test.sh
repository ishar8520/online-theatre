#!/usr/bin/env bash

set -e

docker compose up --abort-on-container-exit
docker compose down
