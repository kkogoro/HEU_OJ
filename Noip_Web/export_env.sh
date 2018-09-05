#!/usr/bin/env bash

export MAIL_SERVER="smtp.mxhichina.com"
export MAIL_PORT=25
export MAIL_USE_TLS=0
export MAIL_USERNAME="no_reply@myvjudge.cn"
export MAIL_PASS="1234567890.123a"
export FLASKY_MAIL_SUBJECT_PREFIX="[HEU Onlie Judge]"
export FLASKY_MAIL_SENDER="no_reply<no_reply@myvjudge.cn>"
export FLASKY_ADMIN="chu849238686@aliyun.com"
export SERVER_NAME="myvjudge.cn"

export CELERY_BROKER_URL="amqp://guest:guest@"+$(RABBITMQ_PORT_5672_TCP_ADDR)+":"+$(RABBITMQ_PORT_5672_TCP_PORT)+"//"
export CELERY_BACKEND_URL="db+mysql://"+$(MYSQL_USER)+":"+$(MYSQL_PASS)+"@"+$(MYSQL_URL)+":"+$(MYSQL_PORT)+"/celery_backend"
