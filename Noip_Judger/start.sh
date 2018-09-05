#!/bin/bash

cd /home/centos/Noip_Judger/

./celery_get_waiting.sh
./celery_judging.sh
./celery_beat.sh
