#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_celery import Celery
import logging
from logging.handlers import RotatingFileHandler

# init db obj and flask obj
db = SQLAlchemy()
flask_celery = Celery()

# create flask app
def create_app(config_name):

    '''
        create app with config
    :param config_name: config settings
    :return: app
    '''

    # use config init app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # config db, celery with app
    db.init_app(app)
    flask_celery.init_app(app)

    # config logger part if not set debug flag
    if not app.debug:
        file_handler = RotatingFileHandler('/tmp/judge.log', 'a', 1*1024*1024, 10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s: %(lineno)d]'))
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('Judge Web StartUp')

    return app