#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta
from kombu import Queue, Exchange
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():

    '''
        config keys and values for whole app
    '''

    API_GET_WAITING = 'http://noip.hrbeu.edu.cn/api/v1.0/status/judge/'
    API_GET_AUTHKEY = 'http://noip.hrbeu.edu.cn/api/v1.0/token'
    API_POST_RESULT = 'http://noip.hrbeu.edu.cn/api/v1.0/status/%d/modify/'
    API_POST_CEINFO = 'http://noip.hrbeu.edu.cn/api/v1.0/status/%d/ce_info/'
    API_POST_RESULT_NOIP = 'http://noip.hrbeu.edu.cn/api/v1.0/status/%d/modify_noip/'
    JUDGE_USERNAME = 'judge1'
    JUDGE_PASSWORD = 'f5eb82444b40d6f71eb1350eaab5353c'
    JUDGE_KEY = 'errorone'

    # about sql query and settings
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # celery settings
    # CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or 'sqla+sqlite:///' + os.path.join(basedir, 'celery-broker.sqlite')
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or 'amqp://guest:guest@localhost:5672//'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_BACKEND_URL') or 'db+mysql://%s:%s@%s:%s/celery_backend' % (os.environ.get('MYSQL_USER'), os.environ.get('MYSQL_PASS'), os.environ.get('MYSQL_ADDR'), os.environ.get('MYSQL_PORT'))
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRO_DATABASE_URL') or 'mysql://%s:%s@%s:%s/online_judge' % (os.environ.get('MYSQL_USER'), os.environ.get('MYSQL_PASS'), os.environ.get('MYSQL_ADDR'), os.environ.get('MYSQL_PORT'))
    CELERY_ALWAYS_EAGER = False
    # 某个程序中出现的队列，在broker中不存在，则立刻创建它
    CELERY_CREATE_MISSING_QUEUES = True
    # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
    CELERYD_MAX_TASKS_PER_CHILD = 100
    CELERYBEAT_SCHEDULE = {
        'get_waiting': {
            'task': 'app.worker.get_waiting',
            # 'schedule': crontab(minute='*/1'),
            # 'args': (1,2),
            'schedule': timedelta(seconds=5)
        },
    }
    CELERY_QUEUES = (
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('get_waiting', Exchange('get_waiting'), routing_key='get_waiting'),
        Queue('judging', Exchange('judging'), routing_key='judging'),
    )

    CELERY_ROUTES = {
        'app.worker.get_waiting': {'queue': 'get_waiting', 'routing_key': 'get_waiting'},
        'app.worker.judging': {'queue': 'judging', 'routing_key': 'judging'},
        'app.worker.judging_noip': {'queue': 'judging', 'routing_key': 'judging'},
    }

    # used for submissions
    GLOBAL_SUBMISSION_STATUS = {
        'Waiting'               : -100,
        'Accepted'              : -1,
        'Compile Error'         : -2,
        'Wrong Answer'          : -3,
        'Presentation Error'    : -4,
        'Runtime Error'         : -5,
        'Time Limit Exceeded'   : -6,
        'Memory Limit Exceeded' : -7,
        'Output Limit Exceeded' : -8,
        'Restricted Function'   : -9,
        'Judging'               : -10,
        'Judge Error'           : -11
    }
    LOCAL_SUBMISSION_STATUS = {
        'Waiting'               : -100,
        'Accepted'              : -1,
        'Compile Error'         : -2,
        'Wrong Answer'          : -3,
        'Presentation Error'    : -4,
        'Runtime Error'         : -5,
        'Time Limit Exceeded'   : -6,
        'Memory Limit Exceeded' : -7,
        'Output Limit Exceeded' : -8,
        'Restricted Function'   : -9,
        'Judging'               : -10,
        'Judge Error'           : -11
    }
    GLOBAL_LANGUAGE = {
        'GCC': 0,
        'G++': 1,
        'C++11': 2,
        'C#': 3,
        'C': 4,
        'C++': 5,
        'Java': 6,
        'Python': 7,
        'Python3': 8,
        'JavaScript': 9
    }
    LOCAL_LANGUAGE = {
        'GCC': 0,
        'G++': 1,
        'Java': 6,
        'Python': 7
    }

    GLOBAL_FILE_TYPE = {
        0: '.c',
        1: '.cpp',
        2: '.cpp',
        3: '.cpp',
        4: '.c',
        5: '.cpp',
        6: '.java',
        7: '.py',
        8: '.py3',
        9: '.js'
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    '''
        make config for development settings
    '''

    # debug setting
    Debug = True



class ProductionConfig(Config):

    '''
        make config for production settings
    '''




# config dicts for manage params
config = {
    'development': DevelopmentConfig,
    'production' : ProductionConfig,

    'default'    : DevelopmentConfig
}
