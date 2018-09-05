#!/usr/bin/env bash

celery -A celery_work beat -f beat.log --loglevel=info &