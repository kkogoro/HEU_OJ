#!/usr/bin/env bash

cd /home/centos/Noip_Web/
gunicorn -c guni.conf manage:app &
