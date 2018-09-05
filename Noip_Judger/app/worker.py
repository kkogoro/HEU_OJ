#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app, render_template
from . import flask_celery
import requests, json, time, commands, base64, os


def get_new():

    '''
        get new judging status
    :return: pending status or None
    '''

    app = current_app._get_current_object()
    r = requests.get(app.config['API_GET_WAITING'], auth=(app.config['JUDGE_KEY'], ''))
    print r.status_code
    if r.status_code == 401:
        r = requests.get(app.config['API_GET_AUTHKEY'], auth=(app.config['JUDGE_USERNAME'], app.config['JUDGE_PASSWORD']))
        app.config['JUDGE_KEY'] = r.json()['token'].decode('utf-8').encode('ascii')
        r = requests.get(app.config['API_GET_WAITING'], auth=(app.config['JUDGE_KEY'], ''))
    print r.status_code
    if r.status_code == 403:
        raise ValueError('Get auth token error')
    print r.json()
    if r.json().has_key(u'id'):
        return True, r.json()
    return False, None


def push_judge_result(id, judge_result):

    '''
        push judge result to web
    :return:
    '''

    app = current_app._get_current_object()
    r = requests.post(app.config['API_POST_RESULT'] % id, json=judge_result, auth=(app.config['JUDGE_KEY'], ''))
    if r.status_code == 401:
        r = requests.get(app.config['API_GET_AUTHKEY'], auth=(app.config['JUDGE_USERNAME'], app.config['JUDGE_PASSWORD']))
        app.config['JUDGE_KEY'] = r.json()['token'].decode('utf-8').encode('ascii')
        r = requests.post(app.config['API_POST_RESULT'] % id, json=judge_result, auth=(app.config['JUDGE_KEY'], ''))
    if r.status_code == 403:
        raise ValueError('Get auth token error')


def push_judge_result_noip(id, judge_result):

    '''
        push judge result to web
    :return:
    '''

    app = current_app._get_current_object()
    r = requests.post(app.config['API_POST_RESULT_NOIP'] % id, json=judge_result, auth=(app.config['JUDGE_KEY'], ''))
    if r.status_code == 401:
        r = requests.get(app.config['API_GET_AUTHKEY'], auth=(app.config['JUDGE_USERNAME'], app.config['JUDGE_PASSWORD']))
        app.config['JUDGE_KEY'] = r.json()['token'].decode('utf-8').encode('ascii')
        r = requests.post(app.config['API_POST_RESULT_NOIP'] % id, json=judge_result, auth=(app.config['JUDGE_KEY'], ''))
    if r.status_code == 403:
        raise ValueError('Get auth token error')


def push_ce_info(id, log_info):

    '''
        push ce info to web
    :return:
    '''

    app = current_app._get_current_object()
    ce_info = {}
    ce_info['submission_id'] = id
    ce_info['info'] = log_info
    r = requests.post(app.config['API_POST_CEINFO'] % id, json=ce_info, auth=(app.config['JUDGE_KEY'], ''))
    if r.status_code == 401:
        r = requests.get(app.config['API_GET_AUTHKEY'], auth=(app.config['JUDGE_USERNAME'], app.config['JUDGE_PASSWORD']))
        app.config['JUDGE_KEY'] = r.json()['token'].decode('utf-8').encode('ascii')
        r = requests.post(app.config['API_POST_CEINFO'] % id, json=ce_info, auth=(app.config['JUDGE_KEY'], ''))
    if r.status_code == 403:
        raise ValueError('Get auth token error')



@flask_celery.task(
    bind=True,
    igonre_result=True,
    expires=10
)
def get_waiting(self):

    '''
        get waiting status
    :return:
    '''

    status, r = get_new()
    while status:
        if r['problem_type'] == 1:
            judging_noip.apply_async(args=[r])
        else:
            judging.apply_async(args=[r])
        time.sleep(1)
        status, r = get_new()
    return None



@flask_celery.task(
    bind=True,
    igonre_result=True,
    default_retry_delay=5,
    max_retries=5
)
def judging(self, status_detail):

    '''
        judge local problem
    :return:
    '''

    app = current_app._get_current_object()
    user_code = base64.decodestring(status_detail['code'])
    file_type = app.config['GLOBAL_FILE_TYPE'][status_detail['language']]
    user_code_filename = str(status_detail['id']) + file_type
    user_code_file = open(user_code_filename, 'w')
    user_code_file.write(user_code)
    user_code_file.close()
    data_filename = str(status_detail['problem_id']) + '/list.conf'
    data_file = open('./data/' + data_filename, 'r')
    file_list = []
    for line in data_file.readlines():
        line = line.strip()
        if len(line) != 0:
            file_list.append('./data/'+str(status_detail['problem_id'])+'/'+line)
    cmd = 'ljudge'
    cmd = cmd + ' --max-cpu-time ' + str(status_detail['max_time'])
    cmd = cmd + ' --max-memory ' + str(status_detail['max_memory']) + 'm'
    cmd = cmd + ' --user-code ' + user_code_filename
    for filename in file_list:
        cmd = cmd + ' --testcase --input ' + filename + '.in'
        cmd = cmd + ' --output ' + filename + '.out'
    print cmd
    status, result = commands.getstatusoutput(cmd)
    os.remove(user_code_filename)
    print status
    print result
    result_json = json.loads(result)
    judge_result = {}
    if status != 0:
        judge_result['status'] = app.config['GLOBAL_SUBMISSION_STATUS']['Judge Error']
        judge_result['exec_time'] = 0
        judge_result['exec_memory'] = 0
        push_judge_result(status_detail['id'], judge_result)
        return None
    else:
        if result_json['compilation']['success'] == False:
            judge_result['status'] = app.config['GLOBAL_SUBMISSION_STATUS']['Compile Error']
            push_ce_info(status_detail['id'], result_json['compilation']['log'])
            judge_result['exec_time'] = 0
            judge_result['exec_memory'] = 0
            push_judge_result(status_detail['id'], judge_result)
            return None
        if result_json['compilation']['log'] != '':
            push_ce_info(status_detail['id'], result_json['compilation']['log'])
        final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']
        final_time = 0
        final_memory = 0
        for testcases in result_json['testcases']:
            if testcases.has_key('memory') and testcases['memory'] > final_memory:
                final_memory = testcases['memory']
            if testcases.has_key('time') and testcases['time'] > final_time:
                final_time = testcases['time']
            if testcases['result'] == 'TIME_LIMIT_EXCEEDED' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Time Limit Exceeded']
                final_time = status_detail['max_time']
            elif testcases['result'] == 'MEMORY_LIMIT_EXCEEDED' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Memory Limit Exceeded']
                final_memory = status_detail['max_memory'] * 1024 * 1024
            elif testcases['result'] == 'NON_ZERO_EXIT_CODE' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'OUTPUT_LIMIT_EXCEEDED' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Output Limit Exceeded']
            elif testcases['result'] == 'FLOAT_POINT_EXCEPTION' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Output Limit Exceeded']
            elif testcases['result'] == 'SEGMENTATION_FAULT' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'RUNTIME_ERROR' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'INTERNAL_ERROR' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'PRESENTATION_ERROR' and final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Presentation Error']
            elif testcases['result'] == 'WRONG_ANSWER':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Wrong Answer']
        judge_result['status'] = final_status
        judge_result['exec_time'] = final_time * 1000
        judge_result['exec_memory'] = final_memory / 1024
        push_judge_result(status_detail['id'], judge_result)
        return None


@flask_celery.task(
    bind=True,
    igonre_result=True,
    default_retry_delay=5,
    max_retries=5
)
def judging_noip(self, status_detail):

    '''
        judge new virtual status
    :return: None
    '''

    app = current_app._get_current_object()
    user_code = base64.decodestring(status_detail['code'])
    file_type = app.config['GLOBAL_FILE_TYPE'][status_detail['language']]
    user_code_filename = str(status_detail['id']) + file_type
    user_code_file = open(user_code_filename, 'w')
    user_code_file.write(user_code)
    user_code_file.close()
    data_filename = str(status_detail['problem_id']) + '/list.conf'
    data_file = open('./data/' + data_filename, 'r')
    file_list = []
    total = 0
    for line in data_file.readlines():
        line = line.strip()
        if len(line) != 0:
            file_list.append('./data/' + str(status_detail['problem_id']) + '/' + line)
            total = total + 1
    cmd = 'ljudge'
    cmd = cmd + ' --max-cpu-time ' + str(status_detail['max_time'])
    cmd = cmd + ' --max-memory ' + str(status_detail['max_memory']) + 'm'
    cmd = cmd + ' --user-code ' + user_code_filename
    for filename in file_list:
        cmd = cmd + ' --testcase --input ' + filename + '.in'
        cmd = cmd + ' --output ' + filename + '.out'
    print cmd
    status, result = commands.getstatusoutput(cmd)
    os.remove(user_code_filename)
    print status
    print result
    result_json = json.loads(result)
    judge_result = {}
    if status != 0:
        judge_result['status'] = app.config['GLOBAL_SUBMISSION_STATUS']['Judge Error']
        judge_result['exec_time'] = 0
        judge_result['exec_memory'] = 0
        push_judge_result(status_detail['id'], judge_result)
        return None
    else:
        if result_json['compilation']['success'] == False:
            judge_result['status'] = app.config['GLOBAL_SUBMISSION_STATUS']['Compile Error']
            push_ce_info(status_detail['id'], result_json['compilation']['log'])
            judge_result['exec_time'] = 0
            judge_result['exec_memory'] = 0
            push_judge_result(status_detail['id'], judge_result)
            return None
        if result_json['compilation']['log'] != '':
            push_ce_info(status_detail['id'], result_json['compilation']['log'])
        final_result = ''
        correct = 0
        for testcases in result_json['testcases']:
            final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']
            final_time = 0
            final_memory = 0
            if testcases.has_key('memory'):
                final_memory = testcases['memory']
            if testcases.has_key('time'):
                final_time = testcases['time']
            if testcases['result'] == 'TIME_LIMIT_EXCEEDED':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Time Limit Exceeded']
                final_time = status_detail['max_time']
            elif testcases['result'] == 'MEMORY_LIMIT_EXCEEDED':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Memory Limit Exceeded']
                final_memory = status_detail['max_memory'] * 1024 * 1024
            elif testcases['result'] == 'NON_ZERO_EXIT_CODE':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'OUTPUT_LIMIT_EXCEEDED':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Output Limit Exceeded']
            elif testcases['result'] == 'FLOAT_POINT_EXCEPTION':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Output Limit Exceeded']
            elif testcases['result'] == 'SEGMENTATION_FAULT':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'RUNTIME_ERROR':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'INTERNAL_ERROR':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Runtime Error']
            elif testcases['result'] == 'PRESENTATION_ERROR' :
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Presentation Error']
            elif testcases['result'] == 'WRONG_ANSWER':
                final_status = app.config['GLOBAL_SUBMISSION_STATUS']['Wrong Answer']
            if final_status == app.config['GLOBAL_SUBMISSION_STATUS']['Accepted']:
                correct = correct + 1
            if final_result != '':
                final_result = final_result + ';'
            final_result = final_result + str(final_status) + ',' + str(final_time*1000) + ',' + str(final_memory/1024)
        judge_result['status'] = correct * 100 / total
        judge_result['child_status'] = final_result
        push_judge_result_noip(status_detail['id'], judge_result)
        return None