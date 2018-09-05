#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import challenge
from .. import db
from ..models import Role, User, Permission, SchoolList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag, ContestUsers, Topic, KeyValue, Challenge, ChallengeRound, ChallengeRoundProblem
from .forms import SubmitForm
from ..decorators import admin_required, permission_required
from datetime import datetime, timedelta
from sqlalchemy.sql import or_
import base64, time

@challenge.route('/', methods=['GET', 'POST'])
def challenge_list():

    '''
        define operation of challenge_list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Challenge.query.order_by(Challenge.challenge_level.asc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    challenge = pagination.items
    return render_template('challenge/challenge_list.html', challenge=challenge, pagination=pagination)


@challenge.route('/<int:challenge_id>/', methods=['GET', 'POST'])
@login_required
def challenge_detail(challenge_id):

    '''
        define operation of challenge detail
    :param challenge_id: challenge_id
    :return:
    '''

    page = request.args.get('page', 1, type=int)
    challenge = Challenge.query.get_or_404(challenge_id)
    if current_user.current_level < challenge.challenge_level and not current_user.can(Permission.MODIFY_SELF_PROBLEM):
        return render_template('challenge/challenge_cannot.html', challenge=challenge)
    pagination = challenge.challenge_round.order_by(ChallengeRound.id.asc()).paginate(page, per_page=current_app.config['FLASKY_USERS_PER_PAGE'])
    round = pagination.items
    return render_template('challenge/challenge_round_list.html', round=round, challenge=challenge, pagination=pagination)


@challenge.route('/round/<int:round_id>', methods=['GET', 'POST'])
@login_required
def round_detail(round_id):

    '''
        define operation of round detail
    :param round_id: round_id
    :return: page
    '''

    round = ChallengeRound.query.get_or_404(round_id)
    challenge = round.challenge
    if current_user.current_level < challenge.challenge_level and not current_user.can(Permission.MODIFY_SELF_PROBLEM):
        return render_template('challenge/challenge_cannot.html', challenge=challenge)
    problems = round.problems.all()
    return render_template('challenge/challenge_round_detail.html', round=round, challenge=challenge, problems=problems)


@challenge.route('/round/<int:round_id>/status', methods=['GET', 'POST'])
@login_required
def round_status_list(round_id):

    '''
        define operation of round submission detail
    :param round_id: round_id
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    round = ChallengeRound.query.get_or_404(round_id)
    challenge = round.challenge
    if current_user.current_level < challenge.challenge_level and not current_user.can(Permission.MODIFY_SELF_PROBLEM):
        return render_template('challenge/challenge_cannot.html', challenge=challenge)
    if current_user.is_admin() or current_user.can(Permission.MODIFY_SELF_PROBLEM):
        pagination = SubmissionStatus.query.filter_by(challenge_id=round_id).order_by(
            SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    else:
        pagination = SubmissionStatus.query.filter_by(challenge_id=round_id, author_username=current_user.username).order_by(
            SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    status = pagination.items
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    return render_template('challenge/challenge_status_list.html', status_list=status_list, language=language,status=status, pagination=pagination, round=round, challenge = challenge)


@challenge.route('/round/<int:round_id>/problem/<int:problem_index>', methods=['GET', 'POST'])
@login_required
def round_problem_detail(round_id, problem_index):

    '''
        define operation of round problems
    :param round_id: round_id
    :param problem_index: problem_index
    :return: page
    '''

    round = ChallengeRound.query.get_or_404(round_id)
    challenge = round.challenge
    if current_user.current_level < challenge.challenge_level and not current_user.can(Permission.MODIFY_SELF_PROBLEM):
        return render_template('challenge/challenge_cannot.html', challenge=challenge)
    problem = round.problems.filter_by(problem_index=problem_index).first_or_404().problem
    return render_template('challenge/round_problem.html', round=round, problem=problem, problem_index=problem_index, challenge=challenge)


@challenge.route('/round/<int:round_id>/problem/<int:problem_index>/submit', methods=['GET', 'POST'])
@login_required
def round_submit(round_id, problem_index):

    '''
        define operation of round problems submit
    :param round_id: round_id
    :param problem_index: problem_index
    :return: page
    '''

    form = SubmitForm()
    round = ChallengeRound.query.get_or_404(round_id)
    challenge = round.challenge
    if current_user.current_level < challenge.challenge_level and not current_user.can(Permission.MODIFY_SELF_PROBLEM):
        return render_template('challenge/challenge_cannot.html', challenge=challenge)
    problem = round.problems.filter_by(problem_index=problem_index).first_or_404().problem
    if form.validate_on_submit():
        submission = SubmissionStatus(submit_time=datetime.utcnow(),
                                      problem_id=problem.id,
                                      status=-100,
                                      exec_time=0,
                                      exec_memory=0,
                                      code_length=len(form.code.data),
                                      language=form.language.data,
                                      code=base64.b64encode(form.code.data.encode('utf-8')),
                                      author_username=current_user.username,
                                      visible=False,
                                      challenge_id=round_id)
        db.session.add(submission)
        db.session.commit()
        return redirect(url_for('challenge.round_status_list', round_id=round_id))
    return render_template('challenge/challenge_submit.html', form=form, problem=problem, problem_index=problem_index, round=round, challenge=challenge)


@challenge.route('/round/<int:round_id>/status/<int:run_id>', methods=['GET', 'POST'])
@login_required
def round_status_detail(round_id, run_id):

    '''
        define operation of round status detail
    :param round_id: round id
    :param run_id: run id
    :return: page
    '''

    round = ChallengeRound.query.get_or_404(round_id)
    challenge = round.challenge
    if current_user.current_level < challenge.challenge_level and not current_user.can(Permission.MODIFY_SELF_PROBLEM):
        return render_template('challenge/challenge_cannot.html', challenge=challenge)
    status = round.submissions.filter_by(id=run_id).first_or_404()
    if current_user.username != status.author_username and (
    not current_user.can(Permission.MODIFY_SELF_PROBLEM)) and current_user.username != round.manager_username:
        return abort(403)
    code = base64.b64decode(status.code).decode('utf-8')
    ce_info = CompileInfo.query.filter_by(submission_id=status.id).first()
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    status_sub = []
    if status.problem.type == True and status.status != -100 and status.status != -10:
        try:
            sub = status.child_status.split(';')
            for i in sub:
                status_sub.append(i.split(','))
        except ValueError, e:
            print "Value error in status %d child_status" % status.id
    return render_template('challenge/round_status_detail.html', status_list=status_list, language=language, status=status, code=code, ce_info=ce_info, round=round, challenge=challenge, status_sub=status_sub)