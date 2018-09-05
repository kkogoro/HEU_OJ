#!/usr/bin/env bash

celery -A celery_work worker -E -f get_waiting.log -l INFO -n get_waiting -Q get_waiting -c 1 &
