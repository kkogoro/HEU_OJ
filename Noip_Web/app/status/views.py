#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, abort, current_app
from flask_login import login_required, current_user
from . import status
from .. import db
from ..models import SubmissionStatus, CompileInfo, Permission, User, Problem
from ..decorators import admin_required, permission_required
from datetime import datetime
from sqlalchemy.sql import or_
import base64, json


@status.route('/', methods=['GET', 'POST'])
@login_required
def status_list():

    '''
        define operations about showing status list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    '''
        2018.7.30 Revised by Techiah
        Add "or current_user.is_teacher()" to allow teachers watch all students'code
    '''
    if current_user.is_super_admin() or current_user.is_teacher():
        pagination = SubmissionStatus.query.order_by(SubmissionStatus.id.desc()).paginate(page,per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    elif current_user.can(Permission.WATCH_OTHER_CODE):
        #pagination = SubmissionStatus.query.order_by(SubmissionStatus.id.desc()).join(User, User.username==SubmissionStatus.author_username).filter(or_(User.school_id == 1, User.school_id == current_user.school_id)).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
        pagination = SubmissionStatus.query.join(Problem, Problem.id == SubmissionStatus.problem_id).filter(or_(Problem.school_id == 1, Problem.school_id == current_user.school_id)).order_by(SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    else:
        '''
            2018.8.1 Revised by Techiah
            Add "author_username=current_user.username" to show students only submissions themselves
        '''
        #print SubmissionStatus.author_username
        pagination = SubmissionStatus.query.filter_by(visible=True, author_username=current_user.username).join(Problem, Problem.id==SubmissionStatus.problem_id).filter(or_(Problem.school_id == 1, Problem.school_id == current_user.school_id)).order_by(SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    status = pagination.items
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]]=k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]]=k
    return render_template('status/status_list.html', status_list=status_list, language=language, status=status, pagination=pagination)


@status.route('/<int:run_id>', methods =['GET', 'POST'])
@login_required
def status_detail(run_id):

    '''
        define operations about showing status detail
    :param run_id: run_id
    :return: page
    '''

    status_detail = SubmissionStatus.query.filter_by(id=run_id).first_or_404()
    if status_detail.visible == False and not current_user.can(Permission.WATCH_OTHER_CODE):
        return abort(404)
    if current_user.username != status_detail.author_username and (not current_user.can(Permission.WATCH_OTHER_CODE)):
        return abort(403)
    '''
		2018.7.30 Revised by Techiah
		This 2 lines are aborted to allow teachers watch all students'code
	'''
    #if status_detail.author.school_id != current_user.school_id and status_detail.author.school_id != 1 and (not current_user.is_admin()):
    #    return abort(403)
    code = base64.b64decode(status_detail.code).decode('utf-8')
    ce_info = CompileInfo.query.filter_by(submission_id=run_id).first()
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[str(current_app.config['LOCAL_SUBMISSION_STATUS'][k])] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    status_sub = []
    if status_detail.problem.type == True and status_detail.status != -100 and status_detail.status != -10 and status_detail.status != -2:
        try:
            sub = status_detail.child_status.split(';')
            for i in sub:
                status_sub.append(i.split(','))
        except ValueError, e:
            print "Value error in status %d child_status" % status_detail.id
    return render_template('status/status.html', status_list=status_list, language=language, status=status_detail, code=code, ce_info=ce_info, status_sub=status_sub)
