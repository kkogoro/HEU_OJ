#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from . import problem
from .. import db
from ..models import SubmissionStatus, Problem, SchoolList, Tag, TagProblem, Permission
from datetime import datetime
from .forms import SubmitForm
from sqlalchemy.sql import or_, func
import base64


@problem.route('/', methods=['GET', 'POST'])
def problem_list():

    '''
        show problem list operation
    :return: page
    '''
    page = request.args.get('page', 1, type=int)
    if current_user.can(Permission.MODIFY_SELF_PROBLEM | Permission.MODIFY_OTHER_PROBLEM):
        pagination = Problem.query.order_by(Problem.id.asc()).paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    elif current_user.can(Permission.MODIFY_SELF_PROBLEM):
        pagination = Problem.query.filter(or_(Problem.school_id==current_user.school_id, Problem.school_id==1)).order_by(Problem.id.asc()).paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    else:
        pagination = Problem.query.filter(or_(Problem.school_id == current_user.school_id, Problem.school_id==1)).filter_by(visible=True).order_by(Problem.id.asc()).paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    problems = pagination.items
    return render_template('problem/problem_list.html', problems=problems, pagination=pagination)


@problem.route('/filter', methods=['GET', 'POST'])
def problem_list_filter():

    '''
        show problem list operation
    :return: page
    '''
    page = request.args.get('page', 1, type=int)
    search_key = request.args.get('key', '', type=unicode)
    remote_id=request.args.get('remote_id', -1, type=int)
    print request.args
    if current_user.can(Permission.MODIFY_SELF_PROBLEM | Permission.MODIFY_OTHER_PROBLEM):
        problems_pagination = Problem.query.order_by(Problem.id.asc())
    elif current_user.can(Permission.MODIFY_SELF_PROBLEM):
        problems_pagination = Problem.query.filter(or_(Problem.school_id==current_user.school_id, Problem.school_id==1)).order_by(Problem.id.asc())
    else:
        problems_pagination = Problem.query.filter(or_(Problem.school_id == current_user.school_id, Problem.school_id == 1)).filter_by(visible=True).order_by(Problem.id.asc())
    if remote_id != -1:
        problems_pagination = problems_pagination.filter(Problem.remote_id == remote_id)
    if search_key != '':
        search_key = search_key.strip()
        search_list = search_key.split('|')
        if len(search_list) == 1:
            problems_pagination = problems_pagination.join(TagProblem, TagProblem.problem_id == Problem.id).join(Tag, Tag.id == TagProblem.tag_id).filter(Tag.tag_name == search_list[0]).group_by(TagProblem.problem_id).having(func.count() == 1)
        else:
            problems_pagination = problems_pagination.join(TagProblem, TagProblem.problem_id==Problem.id).join(Tag, Tag.id==TagProblem.tag_id).filter(or_(Tag.tag_name==search_list[0],Tag.tag_name==search_list[1])).group_by(TagProblem.problem_id).having(func.count() == 2)
        if not current_user.is_admin():
            problems_pagination = problems_pagination.filter(Problem.visible == True)
    pagination = problems_pagination.paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    problems = pagination.items
    return render_template('problem/problem_list.html', problems=problems, pagination=pagination)



@problem.route('/<int:problem_id>', methods=['GET', 'POST'])
def problem_detail(problem_id):

    '''
        show problem details operation
    :param problem_id: problem_id
    :return: page
    '''

    problem = Problem.query.get_or_404(problem_id)
    if problem.school_id != current_user.school_id and problem.school_id != 1 and not current_user.can(Permission.MODIFY_OTHER_CONTEST):
        return abort(404)
    if problem.visible != True and not current_user.can(Permission.MODIFY_SELF_CONTEST):
        return abort(404)
    return render_template('problem/problem.html', problem=problem)


@problem.route('/submit/<int:problem_id>', methods=['GET', 'POST'])
@login_required
def submit(problem_id):

    '''
        operation of submit code
    :param problem_id: problem_id
    :return: page
    '''

    submission = SubmissionStatus()
    #problem = Problem.query.get_or_404(problem_id)
    form = SubmitForm()
    if form.validate_on_submit():
        problem = Problem.query.with_lockmode('update').get(form.problem_id.data)
        if problem is None or (problem.visible == False and not current_user.is_admin()):
            flash("No such problem!")
            return render_template('problem/submit.html', form=form)
        if problem.school_id != current_user.school_id and problem.school_id != 1 and not current_user.can(Permission.MODIFY_OTHER_CONTEST):
            #return abort(404)
            flash("No such problem!")
            return render_template('problem/submit.html', form=form)
        if problem.visible != True and not current_user.can(Permission.MODIFY_SELF_CONTEST):
            #return abort(403)
            flash("No such problem!")
            return render_template('problem/submit.html', form=form)
        submission.submit_time = datetime.utcnow()
        submission.problem_id = form.problem_id.data
        submission.status = -100
        submission.exec_time = 0
        submission.exec_memory = 0
        submission.language = form.language.data
        submission.code_length = len(form.code.data)
        submission.code = base64.b64encode(form.code.data.encode('utf-8'))
        submission.author_username = current_user.username
        submission.visible = True
        submission.submit_ip = request.headers.get('X-Real-IP')
        #submission.child_status = '{}'
        problem.submission_num += 1
        db.session.add(problem)
        db.session.add(submission)
        db.session.commit()
        return redirect(url_for('status.status_list'))
    form.problem_id.data = problem_id
    return render_template('problem/submit.html', form=form)

