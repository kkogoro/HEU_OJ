#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role, Problem, SchoolList

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
        default_school = SchoolList(school_name='default')
        db.session.add(default_school)
        db.session.commit()
        school1 = SchoolList(school_name='school1')
        db.session.add(school1)
        db.session.commit()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):

        '''
            tear down func for test model
        :return: None
        '''

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_404_page(self):

        '''
            test 404 page is good
        :return: None
        '''

        response = self.client.get(url_for('static', filename='styles.css'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(b'你要访问的页面去火星了' in response.data)

    def test_index_page(self):

        '''
            test index page is good
        :return: None
        '''

        response = self.client.get(url_for('admin.admin_index'))
        self.assertTrue(response.status_code == 403)
        self.assertTrue(b'你要前往的页面需要特殊权限' in response.data)
        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        self.assertTrue(b'test2' in response.data)
        response = self.client.get(url_for('admin.admin_index'), follow_redirects=True)
        self.assertTrue(response.status_code == 403)
        self.assertTrue(b'你要前往的页面需要特殊权限' in response.data)
        u.role_id=Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('admin.admin_index'), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'test2' in response.data)

    def test_problem_list(self):

        '''
            test admin problem_list is good
        :return: None
        '''

        response = self.client.get(url_for('admin.problem_list'))
        self.assertTrue(response.status_code == 403)
        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        p = Problem(title='thisisatest')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Problem List' in response.data)
        self.assertTrue(b'thisisatest' in response.data)

    def test_problem_detail(self):

        '''
            test admin problem detail page is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        p = Problem(title='thisisatest')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_detail', problem_id=p.id))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'thisisatest' in response.data)

    def test_add_problem(self):

        '''
            test admin add problem page is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        school = SchoolList(school_name='local')
        db.session.add(school)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_insert'))
        response = self.client.post(url_for('admin.problem_insert'), data={
            'school_id': '1',
            'title': 'hahah',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        self.assertTrue(b'hahah' in response.data)

    def test_edit_problem(self):

        '''
            test admin add problem page is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        school = SchoolList(school_name='local')
        db.session.add(school)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_insert'))
        response = self.client.post(url_for('admin.problem_insert'), data={
            'school_id': '1',
            'title': 'hahah',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        self.assertTrue(b'hahah' in response.data)
        response = self.client.get(url_for('admin.problem_edit', problem_id=1))
        self.assertTrue(b'hahah' in response.data)
        response = self.client.post(url_for('admin.problem_edit', problem_id=1), data={
            'school_id': '1',
            'title': 'hahahhaha',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        self.assertTrue(b'hahahhaha' in response.data)

    def test_upload_file(self):

        '''
            test upload file
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        school = SchoolList(school_name='local')
        db.session.add(school)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.upload_file', problem_id=1))
        self.assertTrue(response.status_code == 404)
        response = self.client.post(url_for('admin.problem_insert'), data={
            'school_id': '1',
            'title': 'hahah',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.upload_file', problem_id=1))
        self.assertTrue(response.status_code == 200)
        response = self.client.post(url_for('admin.upload_file', problem_id=1))
        self.assertTrue(response.status_code == 200)

    def test_tag(self):

        '''
            test tag part
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.tag_insert'), data={
            'tag_name': 'thisisatag'
        }, follow_redirects=True)
        self.assertTrue(b'thisisatag' in response.data)
        response = self.client.post(url_for('admin.tag_insert'), data={
            'tag_name': 'thisisatag'
        }, follow_redirects=True)
        self.assertTrue(b'tag名称已存在' in response.data)
        response = self.client.post(url_for('admin.tag_edit', tag_id=1), data={
            'tag_name': 'thisisatag2'
        }, follow_redirects=True)
        self.assertTrue(b'thisisatag2' in response.data)

    def test_edit_user(self):

        '''
            test user part
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        db.session.add(u2)
        db.session.commit()
        response = self.client.get(url_for('admin.user_list'))
        self.assertTrue(b'test3' in response.data)
        response = self.client.get(url_for('admin.user_detail', username=u2.username))
        self.assertTrue(b'test3' in response.data)
        response = self.client.get(url_for('admin.user_edit', user_id=u2.id))
        self.assertTrue(b'test3' in response.data)
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test4@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(name='Student').first().id,
            'school_id' : 1,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertTrue(b'test4' in response.data)
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test14@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(name='Teacher').first().id,
            'gender': 'Male',
            'school_id': 1,
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertTrue(b'test14' in response.data)

    def test_school(self):

        '''
            test if admin oj part is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.school_status_insert'), data={
            'school_name': 'school_test'
        }, follow_redirects=True)
        self.assertTrue(b'Add school status successful!' in response.data)
        response = self.client.get(url_for('admin.school_list'))
        #print response.data
        self.assertTrue(b'school_test' in response.data)
        response = self.client.get(url_for('admin.school_status', school_id=3))
        self.assertTrue(b'school_test' in response.data)
        response = self.client.get(url_for('admin.school_status_edit', school_id=3))
        self.assertTrue(b'school_test' in response.data)
        response = self.client.post(url_for('admin.school_status_edit', school_id=3), data={
            'school_name': 'school_test2'
        }, follow_redirects=True)
        self.assertTrue(b'school_test2' in response.data)
        self.assertTrue(b'Update school status successful!' in response.data)
        response = self.client.get(url_for('admin.school_status_delete'), follow_redirects=True)
        self.assertTrue(b'No such school in school_list!' in response.data)
        response = self.client.get(url_for('admin.school_status_delete', school_id=4), follow_redirects=True)
        self.assertTrue(b'No such school in school_list!' in response.data)
        response = self.client.get(url_for('admin.school_status_delete', school_id=3), follow_redirects=True)
        self.assertTrue(b'Delete school successful!' in response.data)
        response = self.client.get(url_for('admin.school_list'))
        self.assertFalse(b'school_test' in response.data)

    def test_submission(self):

        '''
            test status part
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        p = Problem(title='test', visible=True)
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': p.id,
            'language': '1',
            'code': 'helloworldsdfsdf'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'G++' in response.data)
        self.client.get(url_for('admin.submission_status_list'))
        self.assertTrue(b'G++' in response.data)
        self.client.get(url_for('admin.submission_status_detail', submission_id=1))
        self.assertTrue(b'G++' in response.data)
        response = self.client.get(url_for('admin.submission_status_edit', submission_id=1))
        response = self.client.post(url_for('admin.submission_status_edit', submission_id=1), data={
            'status': '1',
            'exec_time': '1',
            'exec_memory': '1'
        }, follow_redirects=True)
        self.assertTrue(b'Accepted' in response.data)

    def test_log(self):

        '''
            test log part is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.log_list'))
        self.assertTrue(b'Admin user' in response.data)

    def test_blog(self):

        '''
            test blog part is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.blog_insert'), data={
            'title': 'thisisatest',
            'content': '123456'
        }, follow_redirects=True)
        self.assertTrue(b'thisisatest' in response.data)
        response = self.client.post(url_for('admin.blog_edit', blog_id=1), data={
            'title': 'thisisatestttttt',
            'content': '123456'
        }, follow_redirects=True)
        self.assertTrue(b'thisisatestttttt' in response.data)
        response = self.client.get(url_for('admin.blog_detail', blog_id=1))
        self.assertTrue(b'thisisatestttttt' in response.data)

    def test_contest(self):

        '''
            test contest part is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.contest_list'))
        self.assertTrue(response.status_code == 200)
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test',
        }, follow_redirects=True)
        self.assertTrue(b'指定的比赛管理员用户不存在' in response.data)
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
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test2',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '2',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test3',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '3',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test4',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '3',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'密码保护的比赛密码不能为空' in response.data)
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test5',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:09',
            'type': '5',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_edit', contest_id=1), data={
            'contest_name': 'contest_test6',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:09',
            'type': '5',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_edit', contest_id=1), data={
            'contest_name': 'contest_test7',
            'start_time': '2001-11-11 10:10',
            'school_id': 1,
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_edit', contest_id=1), data={
            'contest_name': 'contest_test8',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '2',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_edit', contest_id=1), data={
            'contest_name': 'contest_test9',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '3',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_edit', contest_id=1), data={
            'contest_name': 'contest_test10',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '3',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'密码保护的比赛密码不能为空' in response.data)
        response = self.client.post(url_for('admin.contest_edit', contest_id=1), data={
            'contest_name': 'contest_test11',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:09',
            'type': '5',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        response = self.client.post(url_for('admin.contest_edit', contest_id=1), data={
            'contest_name': 'contest_test',
            'school_id': 1,
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test',
        }, follow_redirects=True)
        self.assertTrue(b'指定的比赛管理员用户不存在' in response.data)
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'题目不存在' in response.data)
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
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem2'
        }, follow_redirects=True)
        self.assertTrue(b'题目已添加至比赛中' in response.data)
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '2'
        }, follow_redirects=True)
        self.assertTrue(b'添加题目成功' in response.data)
        self.assertTrue(b'problem_test2' in response.data)
        response = self.client.get(url_for('admin.delete_contest_problem', contest_id=1), follow_redirects=True)
        self.assertTrue(b'请指定题目ID' in response.data)
        response = self.client.get(url_for('admin.delete_contest_problem', contest_id=1, problem_id=3), follow_redirects=True)
        self.assertTrue(b'题目列表中不存在该题目' in response.data)
        p = Problem(title='problem_test3')
        db.session.add(p)
        db.session.commit()
        response = self.client.get(url_for('admin.delete_contest_problem', contest_id=1, problem_id=3), follow_redirects=True)
        self.assertTrue(b'比赛题目列表中没有该题目' in response.data)
        response = self.client.get(url_for('admin.delete_contest_problem', contest_id=1, problem_id=2), follow_redirects=True)
        self.assertTrue(b'删除成功' in response.data)