#!/bin/bash

export PYTHONPATH=/opt/app

hypercorn ugc.main:app --bind 0.0.0.0:5002 --reload