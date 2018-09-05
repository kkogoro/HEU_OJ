#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role, SubmissionStatus, CompileInfo, Problem, SchoolList


class APITestCase(unittest.TestCase):

    def setUp(self):

        '''
            set up func for test model
        :return: None
        '''

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        default_school = SchoolList(school_name='default')
        db.session.add(default_school)
        db.session.commit()
        school1 = SchoolList(school_name='school1')
        db.session.add(school1)
        db.session.commit()

    def tearDown(self):

        '''
            tear down func for test model
        :return: None
        '''

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):

        '''
            generate header
        :param username: username or token
        :param password: password
        :return: json
        '''
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):

        '''
            test 404 page is good
        :return: None
        '''

        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['error'] == 'not found')

    def test_bad_auth(self):

        '''
            test bad auth
        :return: None
        '''

        r = Role.query.filter_by(name='Local Judger').first()
        self.assertIsNotNone(r)
        u = User(username='test', email='test@test.com', password='123456', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        response = self.client.get(
            url_for('api.judge_new'),
            headers=self.get_api_headers('test', '1234567'))
        self.assertTrue(response.status_code == 401)

    def test_token_auth(self):

        '''
            test auth with token
        :return: None
        '''

        r = Role.query.filter_by(name='Local Judger').first()
        self.assertIsNotNone(r)
        u = User(username='test', email='test@test.com', password='123456', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # issue a request with a bad token
        response = self.client.get(
            url_for('api.judge_new'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        # get a token
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('test', '123456'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        response = self.client.get(
            url_for('api.judge_new'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_anonymous(self):

        '''
            test anonymous
        :return: None
        '''

        response = self.client.get(
            url_for('api.judge_new'),
            headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 403)

    def test_unconfirmed_account(self):

        '''
            test unconfirmed user
        :return: None
        '''

        r = Role.query.filter_by(name='Local Judger').first()
        self.assertIsNotNone(r)
        u = User(username='test', email='test@test.com', password='123456', role=r)
        db.session.add(u)
        db.session.commit()
        # get new judge with the unconfirmed account
        response = self.client.get(
            url_for('api.judge_new'),
            headers=self.get_api_headers('test', '123456'))
        self.assertTrue(response.status_code == 403)

    def test_judge(self):

        '''
            test during the whole judge
        :return: None
        '''

        r = Role.query.filter_by(name='Local Judger').first()
        self.assertIsNotNone(r)
        u = User(username='test', email='test@test.com', password='123456', confirmed=True, role=r, school_id=2)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': '123456',
            'remember_me': 0
        }, follow_redirects=True)
        p = Problem(title='test', visible=True, school_id=2)
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': '1',
            'language': '1',
            'code': 'helloworldsdfsdf'
        }, follow_redirects=True)
        # get new judge
        response = self.client.get(
            url_for('api.judge_new'),
            headers=self.get_api_headers('test', '123456'))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNone(json_response.get('message'))
        self.assertTrue(response.status_code == 200)
        # add ce info to vaild status
        response = self.client.post(
            url_for('api.add_ce_info', status_id=2),
            headers=self.get_api_headers('test', '123456'),
            data=json.dumps({'info': 'thisistheinfo'})
        )
        self.assertTrue(response.status_code == 404)
        # add ce info with not enough data
        response = self.client.post(
            url_for('api.add_ce_info', status_id=1),
            headers=self.get_api_headers('test', '123456'),
            data=json.dumps({'info': ''})
        )
        self.assertTrue(response.status_code == 400)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(b'Compile_info require full data' in json_response.get('message'))
        # add ce info success
        response = self.client.post(
            url_for('api.add_ce_info', status_id=1),
            headers=self.get_api_headers('test', '123456'),
            data=json.dumps({'info': 'thisistheinfo'})
        )
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # update status to vaild status
        response = self.client.post(
            url_for('api.change_status', status_id=2),
            headers=self.get_api_headers('test', '123456'),
            data=json.dumps({'status': '1', 'exec_time': '0', 'exec_memory': '0'})
        )
        self.assertTrue(response.status_code == 404)
        # update status with no enough data
        response = self.client.post(
            url_for('api.change_status', status_id=1),
            headers=self.get_api_headers('test', '123456'),
            data=json.dumps({'status': '1', 'exec_time': '0', 'exec_memory': ''})
        )
        self.assertTrue(response.status_code == 400)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(b'Status require full data' in json_response.get('message'))
        # update status success
        response = self.client.post(
            url_for('api.change_status', status_id=1),
            headers=self.get_api_headers('test', '123456'),
            data=json.dumps({'status': '-1', 'exec_time': '0', 'exec_memory': '0'})
        )
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        p = Problem.query.get(1)
        self.assertTrue(p.accept_num == 1)

        response = self.client.post(
            url_for('api.change_status_noip', status_id=1),
            headers=self.get_api_headers('test', '123456'),
            data=json.dumps({'status': '100', 'exec_time': '0', 'exec_memory': '0'})
        )
        #print response.data
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        p = Problem.query.get(1)
        self.assertTrue(p.accept_num == 2)

        # get judge status after judge
        response = self.client.get(
            url_for('api.get_status', status_id=1),
            headers=self.get_api_headers('test', '123456'),
        )
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        status = json_response.get('status')
        self.assertIsNotNone(status)

        # get new to judge
        response = self.client.get(
            url_for('api.judge_new'),
            headers=self.get_api_headers('test', '123456'))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(b'No more waiting submissions' in json_response.get('message'))
        self.assertTrue(response.status_code == 200)

