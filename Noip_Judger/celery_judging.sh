#!/usr/bin/env bash

celery -A celery_work worker -E -f judging.log -l INFO -n judging -Q judging -c 2 &
