#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role, Problem, Contest, SchoolList
import time

class FlaskClientTestCase(unittest.TestCase):

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
        self.client = self.app.test_client(use_cookies=True)
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

    def test_contest_admin(self):

        '''
            test contest is good
        :return: None
        '''

        response = self.client.get(url_for('contest.contest_list'))
        self.assertTrue(response.status_code == 200)
        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True, school_id=1)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True, school_id=1)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 1 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id' : 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        #print response.data
        self.assertTrue(b'编辑比赛题目' in response.data)
        # add problem
        p = Problem(title='problem_test', school_id=1)
        db.session.add(p)
        db.session.commit()
        p = Problem(title='problem_test2', school_id=1)
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest_detail
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛描述' in response.data)
        # in contest again
        response = self.client.get(url_for('contest.open_contest_register', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'您已注册' in response.data)
        response = self.client.get(url_for('contest.private_contest_pre_register', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 404)
        response = self.client.get(url_for('contest.private_contest_register', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 404)
        # visit contest_problem list
        response = self.client.get(url_for('contest.contest_problem_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest problem detail
        response = self.client.get(url_for('contest.contest_problem_detail', contest_id=1, problem_index=1001), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest problem detail do not exist
        response = self.client.get(url_for('contest.contest_problem_detail', contest_id=1, problem_index=1009), follow_redirects=True)
        self.assertTrue(response.status_code == 404)
        # submit code
        response = self.client.get(url_for('contest.contest_submit', contest_id=1, problem_index=1001), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        response = self.client.post(url_for('contest.contest_submit', contest_id=1, problem_index=1001), data={
            'language': '1',
            'code': '1234567890.1234586789'
        },follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)
        # visit contest status detail
        response = self.client.get(url_for('contest.contest_status_detail', run_id=1, contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)
        # visit contest rank
        response = self.client.get(url_for('contest.contest_ranklist', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛描述' in response.data)
        response = self.client.get(url_for('contest.contest_status_detail', run_id=1, contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 403)

    def test_contest_user(self):

        '''
            test contest with normal user is good
        :return:
        '''

        response = self.client.get(url_for('contest.contest_list'))
        self.assertTrue(response.status_code == 200)
        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True, school_id=1)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 1 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        # add problem
        p = Problem(title='problem_test')
        db.session.add(p)
        db.session.commit()
        p = Problem(title='problem_test2')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'contest_problem' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        # visit contest_detail
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛描述' in response.data)
        # visit contest problem list
        response = self.client.get(url_for('contest.contest_problem_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest problem detail
        response = self.client.get(url_for('contest.contest_problem_detail', contest_id=1, problem_index=1001),follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # submit code
        response = self.client.post(url_for('contest.contest_submit', contest_id=1, problem_index=1001), data={
            'language': '1',
            'code': '1234567890.1234586789'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛已经结束' in response.data)

    def test_register_contest(self):

        '''
            test if the contest is register contest
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        u3 = User(username='test4', password='123456', email='test4@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 2 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '2',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(b'请确保以下个人信息符合比赛管理员' in response.data)
        response = self.client.get(url_for('contest.private_contest_register', contest_id=1), follow_redirects=True)
        self.assertTrue(b'注册成功' in response.data)
        response = self.client.get(url_for('contest.private_contest_register', contest_id=1), follow_redirects=True)
        self.assertTrue(b'您已注册' in response.data)
        response = self.client.get(url_for('contest.private_contest_pre_register', contest_id=1), follow_redirects=True)
        self.assertTrue(b'您已注册' in response.data)
        response = self.client.get(url_for('contest.password_contest_register', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 404)
        response = self.client.get(url_for('contest.contest_problem_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请等待管理员确认您的参赛请求' in response.data)
        response = self.client.get(url_for('contest.contest_problem_detail', contest_id=1, problem_index=1001), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请等待管理员确认您的参赛请求' in response.data)
        response = self.client.get(url_for('contest.contest_status_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请等待管理员确认您的参赛请求' in response.data)
        response = self.client.get(url_for('contest.contest_ranklist', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请等待管理员确认您的参赛请求' in response.data)
        response = self.client.get(url_for('contest.contest_submit', contest_id=1, problem_index=1001),follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请等待管理员确认您的参赛请求' in response.data)
        response = self.client.get(url_for('contest.contest_status_detail', contest_id=1, run_id=1),follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请等待管理员确认您的参赛请求' in response.data)
        response = self.client.get(url_for('contest.contest_user_check', contest_id=1), follow_redirects=True)
        self.assertTrue(b'你没有权限访问这个页面' in response.data)
        response = self.client.get(url_for('contest.contest_user_checked', contest_id=1), follow_redirects=True)
        self.assertTrue(b'你没有权限访问这个页面' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_user_check', contest_id=1), follow_redirects=True)
        self.assertTrue(b'test3' in response.data)
        self.assertTrue(b'未确认' in response.data)
        response = self.client.get(url_for('contest.contest_user_checked', contest_id=1, user_id=2, flag=1), follow_redirects=True)
        self.assertTrue(b'test3' in response.data)
        self.assertTrue(b'已确认' in response.data)
        response = self.client.get(url_for('contest.contest_user_checked', contest_id=1, user_id=2, flag=0), follow_redirects=True)
        self.assertTrue(b'test3' in response.data)
        self.assertTrue(b'未确认' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test4',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_problem_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请确保以下个人信息符合' in response.data)

    def test_password_contest(self):

        '''
            test if the contest is password protect contest
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 2 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '3',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(b'比赛密码' in response.data)
        response = self.client.post(url_for('contest.password_contest_register', contest_id=1), data={
            'contest_password': 'test'
        }, follow_redirects=True)
        self.assertTrue(b'密码错误' in response.data)
        response = self.client.post(url_for('contest.password_contest_register', contest_id=1), data={
            'contest_password': 'thisisatest'
        }, follow_redirects=True)
        self.assertTrue(b'注册成功' in response.data)
        response = self.client.post(url_for('contest.password_contest_register', contest_id=1), data={
            'contest_password': 'thisisatest'
        }, follow_redirects=True)
        self.assertTrue(b'您已注册' in response.data)
        response = self.client.get(url_for('contest.open_contest_register', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 404)

    def test_onsite_contest(self):

        '''
            test if the contest is password protect contest
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        u3 = User(username='test4', password='123456', email='test4@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 2 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '5',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(b'本场比赛为正式比赛' in response.data)

    def test_ranklist(self):

        '''
            test if the contest ranklist is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 1 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2019-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2'
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        # add problem
        p = Problem(title='problem_test')
        db.session.add(p)
        db.session.commit()
        p = Problem(title='problem_test2')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'contest_problem' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        # submit code
        response = self.client.post(url_for('contest.contest_submit', contest_id=1, problem_index=1001), data={
            'language': '1',
            'code': '1234567890.1234586789'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.submission_status_edit', submission_id=1), data={
            'status': '1',
            'exec_time': '1',
            'exec_memory': '1'
        }, follow_redirects=True)
        self.assertTrue(b'Accepted' in response.data)
        # get ranklist
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_ranklist', contest_id=1),follow_redirects=True)
        self.assertTrue(b'accept' in response.data)
        time.sleep(20)
        response = self.client.get(url_for('contest.contest_ranklist', contest_id=1), follow_redirects=True)
        self.assertTrue(b'accept' in response.data)

    def test_ranklist_admin(self):

        '''
            test if the contest ranklist is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 1 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2019-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2'
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        # add problem
        p = Problem(title='problem_test')
        db.session.add(p)
        db.session.commit()
        p = Problem(title='problem_test2')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'contest_problem' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        # submit code
        response = self.client.post(url_for('contest.contest_submit', contest_id=1, problem_index=1001), data={
            'language': '1',
            'code': '1234567890.1234586789'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.submission_status_edit', submission_id=1), data={
            'status': '1',
            'exec_time': '1',
            'exec_memory': '1'
        }, follow_redirects=True)
        self.assertTrue(b'Accepted' in response.data)
        # get ranklist
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_ranklist_admin', contest_id=1),follow_redirects=True)
        self.assertTrue(b'accept' in response.data)
        time.sleep(20)
        response = self.client.get(url_for('contest.contest_ranklist_admin', contest_id=1), follow_redirects=True)
        self.assertTrue(b'accept' in response.data)

    def test_rejudge_and_sendballoon(self):

        '''
            test rejudge func
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 1 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        # add problem
        p = Problem(title='problem_test')
        db.session.add(p)
        db.session.commit()
        p = Problem(title='problem_test2')
        db.session.add(p)
        db.session.commit()
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest_detail
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛描述' in response.data)
        # submit code
        response = self.client.post(url_for('contest.contest_submit', contest_id=1, problem_index=1001), data={
            'language': '1',
            'code': '1234567890.1234586789'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)
        response = self.client.post(url_for('admin.submission_status_edit', submission_id=1), data={
            'status': '-1',
            'exec_time': '1',
            'exec_memory': '1'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_status_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Accept' in response.data)
        # send balloon
        response = self.client.get(url_for('contest.contest_show_balloon', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Accept' in response.data)
        response = self.client.get(url_for('contest.contest_sent_balloon', contest_id=1, run_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'已发送气球' in response.data)
        self.assertFalse(b'Accept' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_show_balloon', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 403)
        response = self.client.get(url_for('contest.contest_sent_balloon', contest_id=1, run_id=1),follow_redirects=True)
        self.assertTrue(response.status_code == 403)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.rejudge_contest_problem', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'请指定题目ID' in response.data)
        response = self.client.get(url_for('admin.rejudge_contest_problem', contest_id=1, problem_id=3), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'题目列表中不存在该题目' in response.data)
        response = self.client.get(url_for('admin.rejudge_contest_problem', contest_id=1, problem_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'rejudge请求提交成功' in response.data)
        response = self.client.get(url_for('contest.contest_status_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)

    def test_contest_insert_user(self):

        '''
            test if the insert user into contest func is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True, school_id=1)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 5 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '5',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        contest = Contest.query.get(1)
        contest.visible = True
        db.session.add(contest)
        db.session.commit()
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(b'本场比赛为正式比赛' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.contest_insert_user', contest_id=1), data={
            'user_list': 'test3, 2010000, 1, 15555555555, test3, 1234567, test3@test3.com; test3, 2010000, 1, 15555555555, test4, 123456'
        }, follow_redirects=True)
        self.assertTrue(b'输入的用户数据错误' in response.data)
        response = self.client.post(url_for('admin.contest_insert_user', contest_id=1), data={
            'user_list': 'test3, 2010000, 1, 15555555555, test3, 1234567, test3@test3.com; test3, 2010000, 1, 15555555555, test4, 123456, test3@test4.com'
        }, follow_redirects=True)
        self.assertTrue(b'插入用户成功' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '1234567'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(b'已注册并确认' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test4',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(b'已注册并确认' in response.data)

