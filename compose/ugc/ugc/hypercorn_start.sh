#!/bin/bash

export PYTHONPATH=/opt/app

hypercorn repositories.app:app --bind 0.0.0.0:5001 --reload