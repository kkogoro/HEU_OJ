#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import contest
from .. import db
from ..models import Role, User, Permission, SchoolList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag, ContestUsers, Topic, KeyValue, ContestProblem, OIContest
from .forms import PasswordRegisterForm, SubmitForm
from ..decorators import admin_required, permission_required
from datetime import datetime, timedelta
from sqlalchemy.sql import or_
import base64, time
from threading import Thread

def in_contest(contest, user_id):

    '''
        define operation of judging people is in contest
    :param contest: contest obj
    :param user_id: user.id
    :return: None
    '''

    user = contest.users.filter_by(user_id=user_id).first()
    if user is None:
        return False, redirect(url_for('contest.contest_detail', contest_id=contest.id))
    if user.user_confirmed == False:
        flash(u'请等待管理员确认您的参赛请求！')
        return False, redirect(url_for('contest.contest_detail', contest_id=contest.id))
    return True, None


@contest.route('/', methods=['GET', 'POST'])
def contest_list():

    '''
        define operation of contest_list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    if current_user.can(Permission.MODIFY_SELF_CONTEST | Permission.MODIFY_OTHER_CONTEST):
        pagination = Contest.query.order_by(Contest.id.desc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    elif current_user.can(Permission.MODIFY_SELF_CONTEST):
        pagination = Contest.query.filter(or_(Contest.school_id==current_user.school_id, Contest.school_id==1)).order_by(Contest.id.desc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    else:
        pagination = Contest.query.filter(or_(Contest.school_id==current_user.school_id, Contest.school_id==1)).filter_by(visible=True).order_by(Contest.id.desc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    contests = pagination.items
    now = datetime.utcnow()
    return render_template('contest/contest_list.html', contests=contests, pagination=pagination, now=now)


@contest.route('/<int:contest_id>', methods=['GET', 'POST'])
@login_required
def contest_detail(contest_id):

    '''
        define operation of showing a contest
    :param contest_id: contest id
    :return: page
    '''
    contest = Contest.query.get_or_404(contest_id)
    if contest.school_id != current_user.school_id and contest.school_id != 1 and not current_user.can(Permission.MODIFY_OTHER_CONTEST):
        return abort(404)
    if contest.visible != True and not current_user.can(Permission.MODIFY_SELF_CONTEST):
        return abort(403)
    now = datetime.utcnow()
    is_in_contest = contest.users.filter_by(user_id=current_user.id).first()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if contest.manager_username == current_user.username or current_user.can(Permission.MODIFY_SELF_CONTEST):
        if is_in_contest is None:
            return redirect(url_for('contest.open_contest_register', contest_id=contest_id))
        return render_template('contest/contest_detail.html', contest=contest, contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, is_in_contest=is_in_contest)
    if is_in_contest is None:
        if contest.style == 1:
            return redirect(url_for('contest.open_contest_register', contest_id=contest_id))
        elif contest.style == 2 or contest.style == 4:
            flash(u'本场比赛为注册比赛，请先注册!')
            return redirect(url_for('contest.private_contest_pre_register', contest_id=contest_id))
        elif contest.style == 3:
            flash(u'本场比赛为密码认证比赛，请先输入密码进行认证!')
            return redirect(url_for('contest.password_contest_register', contest_id=contest_id))
        elif contest.style == 5:
            flash(u'本场比赛为正式比赛，您无权参加!')
            return redirect(url_for('contest.contest_list'))
    return render_template('contest/contest_detail.html', contest=contest ,contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, is_in_contest=is_in_contest)


@contest.route('/<int:contest_id>/open_register', methods=['GET', 'POST'])
@login_required
def open_contest_register(contest_id):

    '''
        define operation of open contest register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.style != 1 and contest.manager_username != current_user.username and (not current_user.is_admin()):
        abort(404)
    if contest.users.filter_by(user_id=current_user.id).first() is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    contest_user = ContestUsers(
        user_id=current_user.id,
        contest_id=contest_id,
        realname=current_user.realname,
        address=current_user.address,
        school_id=current_user.school_id,
        student_num=current_user.student_num,
        phone_num=current_user.phone_num,
        user_confirmed=True,
        register_time=datetime.utcnow()
    )
    db.session.add(contest_user)
    db.session.commit()
    return redirect(url_for('contest.contest_detail', contest_id=contest_id))


@contest.route('/<int:contest_id>/private_pre_register', methods=['GET', 'POST'])
@login_required
def private_contest_pre_register(contest_id):

    '''
        define operation of private contest pre register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.style != 2 and contest.style != 4:
        abort(404)
    is_in_contest = contest.users.filter_by(user_id=current_user.id).first()
    if is_in_contest is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    return render_template('contest/contest_private_register.html', contest=contest, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, contest_id=contest_id, is_in_contest=is_in_contest)


@contest.route('/<int:contest_id>/private_register', methods=['GET', 'POST'])
@login_required
def private_contest_register(contest_id):

    '''
        define operation of private contest register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.style != 2 and contest.style != 4:
        abort(404)
    if contest.users.filter_by(user_id=current_user.id).first() is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    contest_user = ContestUsers(
        user_id=current_user.id,
        contest_id=contest_id,
        realname=current_user.realname,
        address=current_user.address,
        school_id=current_user.school_id,
        student_num=current_user.student_num,
        phone_num=current_user.phone_num,
        user_confirmed=False,
        register_time=datetime.utcnow()
    )
    db.session.add(contest_user)
    db.session.commit()
    flash(u'注册成功, 请等待比赛管理员同意您的参赛请求')
    return redirect(url_for('contest.contest_detail', contest_id=contest_id))


@contest.route('/<int:contest_id>/password_register', methods=['GET', 'POST'])
@login_required
def password_contest_register(contest_id):

    '''
        define operation of private contest pre register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.style != 3:
        abort(404)
    is_in_contest = contest.users.filter_by(user_id=current_user.id).first()
    if is_in_contest is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    form = PasswordRegisterForm()
    if form.validate_on_submit():
        if form.contest_password.data == contest.password:
            contest_user = ContestUsers(
                user_id=current_user.id,
                contest_id=contest_id,
                realname=current_user.realname,
                address=current_user.address,
                school_id=current_user.school_id,
                student_num=current_user.student_num,
                phone_num=current_user.phone_num,
                user_confirmed=True,
                register_time=datetime.utcnow()
            )
            db.session.add(contest_user)
            db.session.commit()
            flash(u'注册成功!')
            return redirect(url_for('contest.contest_detail', contest_id=contest_id))
        else:
            flash(u'密码错误!')
            return redirect(url_for('contest.password_contest_register', contest_id=contest_id))
    return render_template('contest/contest_password_register.html', contest=contest, form=form, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, contest_id=contest_id, is_in_contest=is_in_contest)


@contest.route('/<int:contest_id>/checking', methods=['GET', 'POST'])
@login_required
def contest_user_check(contest_id):

    '''
        define operation about admin confirm contest user
    :param contest_id: contest_id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    page = request.args.get('page', 1, type=int)
    if contest.manager_username != current_user.username and (current_user.is_admin() is False):
        flash(u"你没有权限访问这个页面！")
        abort(403)
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    checked_num = contest.users.filter_by(user_confirmed=True).count()
    unchecked_num = contest.users.filter_by(user_confirmed=False).count()
    pagination = contest.users.order_by(ContestUsers.user_confirmed.asc(), ContestUsers.register_time.asc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    users = pagination.items
    return render_template('contest/contest_user_check.html', contest=contest, contest_id=contest_id, pagination=pagination, users=users, checked_num=checked_num, unchecked_num=unchecked_num, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)


@contest.route('/<int:contest_id>/checked', methods=['GET', 'POST'])
@login_required
def contest_user_checked(contest_id):

    '''
        define operation about confirm or unconfirm user
    :param contest_id: contest_id
    :return: Null
    '''
    user_id = request.args.get('user_id', -1, type=int)
    flag = request.args.get('flag', 1, type=int)
    contest = Contest.query.get_or_404(contest_id)
    if contest.manager_username != current_user.username and (current_user.is_admin() is False):
        flash(u"你没有权限访问这个页面")
        abort(403)
    contest_user = ContestUsers.query.filter_by(user_id=user_id, contest_id=contest_id).first()
    if flag == 1:
        contest_user.user_confirmed = True
    else:
        contest_user.user_confirmed = False
    db.session.add(contest_user)
    db.session.commit()
    return redirect(url_for('contest.contest_user_check', contest_id=contest_id))


@contest.route('/<int:contest_id>/problems', methods=['GET', 'POST'])
@login_required
def contest_problem_list(contest_id):

    '''
        define operation about contest problem list
    :param contest_id: contest_id
    :return:
    '''
    contest = Contest.query.get_or_404(contest_id)
    now = datetime.utcnow()
    is_in_contest = contest.users.filter_by(user_id=current_user.id).first()
    problems = contest.problems.all()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if contest.manager_username == current_user.username or current_user.is_admin():
        return render_template('contest/contest_problem_list.html', contest=contest, problems=problems, contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, is_in_contest=is_in_contest)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    if contest.start_time > now:
        flash(u'比赛尚未开始，请等待！')
        return redirect(url_for('contest.contest_detail',contest_id=contest_id))
    return render_template('contest/contest_problem_list.html', contest=contest, problems=problems ,contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, is_in_contest=is_in_contest)


@contest.route('/<int:contest_id>/problem/<int:problem_index>', methods=['GET', 'POST'])
@login_required
def contest_problem_detail(contest_id, problem_index):

    '''
        define operation about showing contest problem detail
    :param contest_id: contest_id
    :param problem_index: problem_index
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    now = datetime.utcnow()
    if contest.start_time > now and current_user.username != contest.manager_username and (not current_user.is_admin()):
        flash(u'比赛尚未开始，请等待！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if not result[0]:
        return result[1]
    problem = contest.problems.filter_by(problem_index=problem_index).first_or_404().problem
    return render_template('contest/contest_problem.html', contest=contest, problem=problem, problem_index=problem_index, contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)


@contest.route('/<int:contest_id>/status', methods=['GET', 'POST'])
@login_required
def contest_status_list(contest_id):

    '''
        define operations about showing contest status
    :param contest_id: contest_id
    :return: page
    '''
    global table
    page = request.args.get('page', 1, type=int)
    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    if contest.type is False:  # ACM Rule
        if current_user.is_admin() or current_user.username == contest.manager_username:
            pagination = SubmissionStatus.query.filter_by(contest_id=contest_id).order_by( SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
        else:
            pagination = SubmissionStatus.query.filter_by(contest_id=contest_id, author_username=current_user.username).order_by(SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
        status = pagination.items
        now = datetime.utcnow()
        sec_now = time.mktime(now.timetuple())
        sec_init = time.mktime(contest.start_time.timetuple())
        sec_end = time.mktime(contest.end_time.timetuple())
        status_list = {}
        language = {}
        for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
            status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
        for k in current_app.config['LOCAL_LANGUAGE'].keys():
            language[current_app.config['LOCAL_LANGUAGE'][k]] = k
        return render_template('contest/contest_status_list.html', rule=False, status_list=status_list, language=language, status=status, pagination=pagination, contest_id=contest_id, contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)
    else :#OI Rule --finished
        now = datetime.utcnow()
        language = {}
        for k in current_app.config['LOCAL_LANGUAGE'].keys():
            language[current_app.config['LOCAL_LANGUAGE'][k]] = k
        sec_now = time.mktime(now.timetuple())
        sec_init = time.mktime(contest.start_time.timetuple())
        sec_end = time.mktime(contest.end_time.timetuple())
        problem_indexes = ContestProblem.query.filter_by(contest_id=contest_id).order_by(ContestProblem.problem_index)
        if current_user.is_admin() or current_user.username == contest.manager_username:
            problem_num = {}
            for index in problem_indexes:
                problem_num[index.problem_id] = index.problem_index

            submit_who = {}
            pagination = OIContest.query.filter_by(contest_id=contest_id)
            who = ContestUsers.query.filter_by(contest_id=contest_id)

            for one in who:
                submit_who[one.user_id] = one.user.username
            pagination = pagination.order_by(OIContest.problem_id).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
            status = pagination.items
            return render_template('contest/contest_status_list.html', rule=True, contest_id=contest_id,
                                   contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end, status=status,
                                   language=language, pagination=pagination,problem_num=problem_num,submit_who=submit_who)

        else:
            pagination = OIContest.query.filter_by(contest_id=contest_id, user_id=current_user.id)
            table = []
            for index in problem_indexes:
                flag = False
                for submit in pagination:
                    if index.problem_id == submit.problem_id:
                        table.append((index.problem_index, True, submit.language, submit.id))
                        flag = True
                        break
                if not flag:
                    table.append((index.problem_index, False))
            return render_template('contest/contest_status_list.html', rule=True, contest_id=contest_id,
                                   contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end, table=table, language=language)


@contest.route('/<int:contest_id>/problem/<int:problem_index>/submit', methods=['GET', 'POST'])
@login_required
def contest_submit(contest_id, problem_index):

    '''
        define operation about submit code of the contest
    :param contest_id:
    :param problem_index:
    :return:
    '''

    form = SubmitForm()
    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    now = datetime.utcnow()
    if contest.start_time > now and current_user.username != contest.manager_username and (not current_user.is_admin()):
        flash(u'比赛尚未开始，请等待！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    if contest.end_time < now and current_user.username != contest.manager_username and (not current_user.is_admin()):
        flash(u'比赛已经结束，无法提交代码！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    problem = contest.problems.filter_by(problem_index=problem_index).first_or_404().problem
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if form.validate_on_submit():
        if contest.type is False:#ACM Rule
            submission = SubmissionStatus(submit_time = datetime.utcnow(),
                                          problem_id = problem.id,
                                          status = -100,
                                          exec_time = 0,
                                          exec_memory = 0,
                                          code_length = len(form.code.data),
                                          language = form.language.data,
                                          code = base64.b64encode(form.code.data.encode('utf-8')),
                                          author_username = current_user.username,
                                          visible = False,
                                          contest_id = contest_id)
            db.session.add(submission)
            db.session.commit()
            return redirect(url_for('contest.contest_status_list',contest_id=contest_id))
        else :#OI Rule
            oisubmission = OIContest.query.filter_by(contest_id=contest.id,user_id=current_user.id,problem_id = problem.id).first();
            if oisubmission is None:
                oisubmission = OIContest(contest_id=contest.id,
                                         user_id=current_user.id,
                                         problem_id = problem.id,
                                         language=form.language.data,
                                         code=base64.b64encode(form.code.data.encode('utf-8')))
            else :
                oisubmission.language = form.language.data
                oisubmission.code = base64.b64encode(form.code.data.encode('utf-8'))
            db.session.add(oisubmission)
            db.session.commit()
            flash(u'提交代码成功！')
            return redirect(url_for('contest.contest_problem_list', contest_id=contest_id))
    return render_template('contest/contest_submit.html', form=form, problem=problem, problem_index=problem_index, contest_id=contest_id, contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)


@contest.route('/<int:contest_id>/status/<int:run_id>', methods=['GET', 'POST'])
@login_required
def contest_status_detail(run_id, contest_id):

    '''
        define operations of showing status detail
    :param run_id:
    :param contest_id:
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    if contest.type is False:  # ACM Rule
        status = contest.submissions.filter_by(id=run_id).first_or_404()
        if current_user.username != status.author_username and (not current_user.can(Permission.MODIFY_SELF_CONTEST)) and current_user.username != contest.manager_username:
            return abort(403)
        code=base64.b64decode(status.code).decode('utf-8')
        ce_info = CompileInfo.query.filter_by(submission_id=status.id).first()
        now = datetime.utcnow()
        sec_now = time.mktime(now.timetuple())
        sec_init = time.mktime(contest.start_time.timetuple())
        sec_end = time.mktime(contest.end_time.timetuple())
        status_list = {}
        language = {}
        for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
            status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
        for k in current_app.config['LOCAL_LANGUAGE'].keys():
            language[current_app.config['LOCAL_LANGUAGE'][k]] = k
        return render_template('contest/contest_status_detail.html', status_list=status_list, language=language, status=status, code=code, ce_info=ce_info, contest_id=contest_id, contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)
    else :#OI Rule -- not finished
        status = OIContest.query.filter_by(id=run_id).first_or_404()
        if current_user.id != status.user_id and (not current_user.can(Permission.MODIFY_SELF_CONTEST)) and current_user.username != contest.manager_username:
            return abort(403)
        code = base64.b64decode(status.code).decode('utf-8')
        now = datetime.utcnow()
        sec_now = time.mktime(now.timetuple())
        sec_init = time.mktime(contest.start_time.timetuple())
        sec_end = time.mktime(contest.end_time.timetuple())
        language = {}
        for k in current_app.config['LOCAL_LANGUAGE'].keys():
            language[current_app.config['LOCAL_LANGUAGE'][k]] = k
        problem_index = ContestProblem.query.filter_by(contest_id=status.contest_id, problem_id= status.problem_id).first().problem_index
        username = User.query.filter_by(id=status.user_id).first().username
        return render_template('contest/contest_status_detail.html', language=language, username=username,
                               status=status, code=code, contest_id=contest_id, contest=contest,
                               sec_now=sec_now, sec_init=sec_init, sec_end=sec_end, problem_index=problem_index)

def OIRun(contest_id):
    '''
        define operation to Run OI contest submission
    :param contest_id:
    :return:
    '''
    contest = Contest.query.filter_by(id=contest_id).first()
    if contest is None or contest.type is False:
        return


    submit_who = {}
    users = ContestUsers.query.filter_by(contest_id=contest_id).all()
    for user in users:
        submit_who[user.user_id] = user.user.username
    submits = OIContest.query.filter_by(contest_id=contest_id).all()
    for one in submits:
        submission = SubmissionStatus(submit_time=datetime.utcnow(),
                                      problem_id=one.problem_id,
                                      status=-100,
                                      exec_time=0,
                                      exec_memory=0,
                                      code_length=len(one.code),
                                      language=one.language,
                                      code=one.code,
                                      author_username=submit_who[one.user_id],
                                      visible=False,
                                      contest_id=contest_id)
        db.session.add(submission)
    db.session.commit()
    return

def OICalc(contest_id):
    '''
           define operation to calculate the ranklist
       :param contest_id:
       :return:
       '''
    '''
            data_struct:
            ranklist = [{'username': (str), 'total_score': (Float), 'submission_detail': {problem_index : {'score'(Float)} }}]
    '''
    ranklists_table_in_database = KeyValue.query.filter_by(key='contest_rank_%s' % str(contest_id)).first()

    if ranklists_table_in_database is None:
        return False
    if ranklists_table_in_database.value != '':
        return True
    contest = Contest.query.filter_by(id=contest_id).first()
    submission = SubmissionStatus.query.filter_by(contest_id=contest_id).all()
    for submit in submission :
        if submit.status==-100 or submit.status==-10 or submit.status==-11:
            return False
    competitors = ContestUsers.query.filter_by(contest_id=contest_id).all()

    ranklists = []
    index = {}
    problem_indexes = ContestProblem.query.filter_by(contest_id=contest_id).order_by(ContestProblem.problem_index)
    problem_num = {}
    for ind in problem_indexes:
        problem_num[ind.problem_id] = ind.problem_index
    for competitor in competitors:
        if competitor.user.is_admin() or contest.manager_username == competitor.user.username:
            continue
        index[competitor.user.username] = len(ranklists)
        '''
            2018.8.2 Revised by Techiah
            'username':competitor.user.username  ->  'username':str(competitor.user,realname).decode('utf-8')
        '''
        ranklists.append( { 'username': str(competitor.user.realname).decode('utf-8'), 'total_score': 0.0, 'submission_detail':{} } )

    for one in submission:
        if one.status >=0:
            if index.get(one.author_username) is None:
                continue
            ranklists[index[one.author_username]]['submission_detail'][problem_num[one.problem_id]] = one.status
            ranklists[index[one.author_username]]['total_score'] += one.status

    ranklists.sort(cmp=cmp_oirank)

    # generate html ranklist
    ranklist_table = ''
    for i, ranklist in enumerate(ranklists):
        ranklist_table += '<tr><td>'
        ranklist_table += str(i + 1)
        ranklist_table += '</td><td>'
        ranklist_table += ranklist['username']
        ranklist_table += '</td><td>'
        ranklist_table += str(ranklist['total_score'])
        ranklist_table += '</td>'
        for problem in problem_indexes:
                #ranklist['submission_detail']:
            ranklist_table += '<td>'
            if ranklist['submission_detail'].get(problem.problem_index) is None:
                ranklist_table += '0.00'
            else:
                ranklist_table += '%.2f' % ranklist['submission_detail'].get(problem.problem_index)
            ranklist_table += '</td>'
        ranklist_table += '</tr>'
    ranklists_table_in_database.value = ranklist_table
    db.session.add(ranklists_table_in_database)
    db.session.commit()
    return True

@contest.route('/<int:contest_id>/ranklist', methods=['GET', 'POST'])
@login_required
def contest_ranklist(contest_id):

    '''
        define operation of showing ranklist
    :param contest_id: contest_id
    :return: page
    '''

    '''
        data_struct:
        ranklist = [{username': (str), 'total_ac': (int), 'total_time': (int), 'submission_detail': {problem_index : {'submission_num': (int), 'ac': bool, 'first_blood': bool, 'time': (int)}}}]
    '''

    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())

    if contest.type is False:  # ACM Rule
        problems = contest.problems.all()
        ranklists_table_in_database = KeyValue.query.filter_by(key='contest_rank_%s' % str(contest.id)).first()
        # frozen rank setting
        if contest.rank_frozen:
            delay = timedelta(hours=1)
        else:
            delay = timedelta(hours=0)
        if contest.end_time - delay < now or contest.last_generate_rank + timedelta(seconds=10) > now:
            if ranklists_table_in_database is not None:
                ranklists = ranklists_table_in_database.value
                return render_template('contest/contest_ranklist.html', ranklists=ranklists, problems=problems, contest=contest, contest_id=contest_id, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)
        users = contest.users.all()
        ranklists = []
        for user in users:
            if user.user.is_admin() or contest.manager_username==user.user.username:
                continue
            user_total = {}
            user_total['username'] = user.user.username
            user_total['realname'] = user.realname if user.realname else user.user.nickname
            user_total['submission_detail'] = {}
            user_total['total_time'] = 0
            user_total['total_ac'] = 0
            for problem in problems:
                status = contest.submissions.filter_by(problem_id=problem.problem_id, author_username=user_total['username']).order_by(SubmissionStatus.id.asc()).all()
                problem_detail = {}
                problem_detail['submission_num'] = 0
                problem_detail['ac'] = False
                problem_detail['first_blood'] = False
                problem_detail['time'] = 0
                for item in status:
                    if item.status == -1:
                        problem_detail['ac'] = True
                        user_total['total_ac'] += 1
                        problem_detail['time'] = problem_detail['submission_num'] * 20 + (item.submit_time - contest.start_time).seconds / 60
                        user_total['total_time'] += problem_detail['time']
                        problem_detail['submission_num'] += 1
                        break
                    else:
                        problem_detail['submission_num'] += 1
                user_total['submission_detail'][problem.problem_index] = problem_detail
            ranklists.append(user_total)
        for problem in problems:
            submissions = contest.submissions.filter_by(problem_id=problem.problem_id, status=current_app.config['LOCAL_SUBMISSION_STATUS']['Accepted']).order_by(SubmissionStatus.id.asc()).limit(20)
            flag = False
            for submission in submissions:
                for user_total in ranklists:
                    if user_total['username'] == submission.author_username:
                        user_total['submission_detail'][problem.problem_index]['first_blood'] = True
                        flag = True
                        break
                if flag:
                    break
        ranklists.sort(cmp=cmp_ranklist)
        # generate html ranklist
        ranklist_table = ''
        for i, ranklist in enumerate(ranklists):
            ranklist_table += '<tr><td>'
            ranklist_table += str(i+1)
            ranklist_table += '</td><td>'
            ranklist_table += ranklist['realname']
            ranklist_table += '</td><td>'
            ranklist_table += str(ranklist['total_ac'])
            ranklist_table += '</td><td>'
            ranklist_table += str(ranklist['total_time'])
            ranklist_table += '</td>'
            for problem in ranklist['submission_detail']:
                ranklist_table += '<td '
                if ranklist['submission_detail'][problem]['first_blood']:
                    ranklist_table += 'class="firstaccept">'
                elif ranklist['submission_detail'][problem]['ac']:
                    ranklist_table += 'class="accept">'
                elif ranklist['submission_detail'][problem]['submission_num'] > 0:
                    ranklist_table += 'class="wrong">'
                if ranklist['submission_detail'][problem]['submission_num'] > 0:
                    ranklist_table += str(ranklist['submission_detail'][problem]['submission_num'])
                else:
                    ranklist_table += '-'
                ranklist_table += '/'
                if ranklist['submission_detail'][problem]['ac']:
                    ranklist_table += str(ranklist['submission_detail'][problem]['time'])
                else:
                    ranklist_table += '--'
                ranklist_table += '</td>'
            ranklist_table += '</tr>'

        if ranklists_table_in_database is None:
            newKV = KeyValue(key='contest_rank_%s'% str(contest.id), value=ranklist_table)
            contest.last_generate_rank = now
            db.session.add(newKV)
            db.session.add(contest)
            db.session.commit()
        else:
            ranklists_table_in_database.value = ranklist_table
            contest.last_generate_rank = now
            db.session.add(ranklists_table_in_database)
            db.session.add(contest)
            db.session.commit()
        return render_template('contest/contest_ranklist.html', ranklists=ranklist_table, problems=problems, contest=contest, contest_id=contest_id, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)
    else : #OI Rule statement 1: not finished; 2:finished but not judged; 3:finished and judged
        if contest.end_time >= now:
            return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id, sec_now=sec_now, sec_init=sec_init,
                                   sec_end=sec_end, statement=1)
        else :
            ranklists_table_in_database = KeyValue.query.filter_by(key='contest_rank_%s' % str(contest.id)).first()
            if ranklists_table_in_database is None:
                newKV = KeyValue(key='contest_rank_%s' % str(contest.id), value='')
                db.session.add(newKV)
                db.session.commit()
                #First time visit to run all judges of the contest
                #make a thread to run and calculate ranklist
                #thread = Thread(target=OIRun, args=[contest_id])
                OIRun(contest.id)
                return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id,
                                       sec_now=sec_now, sec_init=sec_init,
                                       sec_end=sec_end, statement=2)
            else :
                if ranklists_table_in_database.value == '':
                    OICalc(contest_id)
                    return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id,
                                           sec_now=sec_now, sec_init=sec_init,
                                           sec_end=sec_end, statement=2)
                else :
                    if contest.rank_frozen:
                        return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id,
                                           sec_now=sec_now, sec_init=sec_init,
                                           sec_end=sec_end, statement=3, rank_frozen=True, value=ranklists_table_in_database.value)
                    else :
                        problems = ContestProblem.query.filter_by(contest_id=contest_id).order_by(
                            ContestProblem.problem_index)
                        return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id,
                                               sec_now=sec_now, sec_init=sec_init,
                                               sec_end=sec_end, statement=3, rank_frozen=False, problems=problems,
                                               value=ranklists_table_in_database.value)


@contest.route('/<int:contest_id>/ranklist_admin', methods=['GET', 'POST'])
@login_required
def contest_ranklist_admin(contest_id):

    '''
        define operation of showing ranklist
    :param contest_id: contest_id
    :return: page
    '''

    '''
        data_struct:
        ranklist = [{username': (str), 'total_ac': (int), 'total_time': (int), 'submission_detail': {problem_index : {'submission_num': (int), 'ac': bool, 'first_blood': bool, 'time': (int)}}}]
    '''

    contest = Contest.query.get_or_404(contest_id)
    if current_user.username != contest.manager_username and (not current_user.can(Permission.MODIFY_SELF_CONTEST)):
        return redirect(url_for('contest.contest_ranklist', contest_id=contest.id))
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if contest.type is False:  # ACM Rule
        problems = contest.problems.all()
        ranklists_table_in_database = KeyValue.query.filter_by(key='contest_rank_%s_admin' % str(contest.id)).first()
        users = contest.users.all()
        ranklists = []
        for user in users:
            if user.user.is_admin() or contest.manager_username==user.user.username:
                continue
            user_total = {}
            user_total['username'] = user.user.username
            user_total['realname'] = user.realname if user.realname else user.user.nickname
            user_total['submission_detail'] = {}
            user_total['total_time'] = 0
            user_total['total_ac'] = 0
            for problem in problems:
                status = contest.submissions.filter_by(problem_id=problem.problem_id, author_username=user_total['username']).order_by(SubmissionStatus.id.asc()).all()
                problem_detail = {}
                problem_detail['submission_num'] = 0
                problem_detail['ac'] = False
                problem_detail['first_blood'] = False
                problem_detail['time'] = 0
                for item in status:
                    if item.status == -1:
                        problem_detail['ac'] = True
                        user_total['total_ac'] += 1
                        problem_detail['time'] = problem_detail['submission_num'] * 20 + (item.submit_time - contest.start_time).seconds / 60
                        user_total['total_time'] += problem_detail['time']
                        problem_detail['submission_num'] += 1
                        break
                    else:
                        problem_detail['submission_num'] += 1
                user_total['submission_detail'][problem.problem_index] = problem_detail
            ranklists.append(user_total)
        for problem in problems:
            submissions = contest.submissions.filter_by(problem_id=problem.problem_id, status=current_app.config['LOCAL_SUBMISSION_STATUS']['Accepted']).order_by(SubmissionStatus.id.asc()).limit(20)
            flag = False
            for submission in submissions:
                for user_total in ranklists:
                    if user_total['username'] == submission.author_username:
                        user_total['submission_detail'][problem.problem_index]['first_blood'] = True
                        flag = True
                        break
                if flag:
                    break
        ranklists.sort(cmp=cmp_ranklist)
        # generate html ranklist
        ranklist_table = ''
        for i, ranklist in enumerate(ranklists):
            ranklist_table += '<tr><td>'
            ranklist_table += str(i+1)
            ranklist_table += '</td><td>'
            ranklist_table += ranklist['realname']
            ranklist_table += '</td><td>'
            ranklist_table += str(ranklist['total_ac'])
            ranklist_table += '</td><td>'
            ranklist_table += str(ranklist['total_time'])
            ranklist_table += '</td>'
            for problem in ranklist['submission_detail']:
                ranklist_table += '<td '
                if ranklist['submission_detail'][problem]['first_blood']:
                    ranklist_table += 'class="firstaccept">'
                elif ranklist['submission_detail'][problem]['ac']:
                    ranklist_table += 'class="accept">'
                elif ranklist['submission_detail'][problem]['submission_num'] > 0:
                    ranklist_table += 'class="wrong">'
                if ranklist['submission_detail'][problem]['submission_num'] > 0:
                    ranklist_table += str(ranklist['submission_detail'][problem]['submission_num'])
                else:
                    ranklist_table += '-'
                ranklist_table += '/'
                if ranklist['submission_detail'][problem]['ac']:
                    ranklist_table += str(ranklist['submission_detail'][problem]['time'])
                else:
                    ranklist_table += '--'
                ranklist_table += '</td>'
            ranklist_table += '</tr>'
        return render_template('contest/contest_ranklist.html', ranklists=ranklist_table, problems=problems, contest=contest, contest_id=contest_id, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)
    else :#OI Rule
        if contest.end_time >= now:
            return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id, sec_now=sec_now, sec_init=sec_init,
                                   sec_end=sec_end, statement=1)
        else :
            ranklists_table_in_database = KeyValue.query.filter_by(key='contest_rank_%s' % str(contest.id)).first()
            if ranklists_table_in_database is None:
                newKV = KeyValue(key='contest_rank_%s' % str(contest.id), value='')
                db.session.add(newKV)
                db.session.commit()
                #First time visit to run all judges of the contest
                #make a thread to run and calculate ranklist
                thread = Thread(target=OIRun, args=[contest.id])
                return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id,
                                       sec_now=sec_now, sec_init=sec_init,
                                       sec_end=sec_end, statement=2)
            else :
                if ranklists_table_in_database.value == '':
                    OICalc(contest.id)
                    return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id,
                                           sec_now=sec_now, sec_init=sec_init,
                                           sec_end=sec_end, statement=2)
                else :
                    return render_template('contest/contest_ranklist.html', contest=contest, contest_id=contest_id,
                                           sec_now=sec_now, sec_init=sec_init,
                                           sec_end=sec_end, statement=3, rank_frozen=False,
                                           value=ranklists_table_in_database.value)


def cmp_ranklist(a, b):

    '''
        define operation of cmp two ranklist item
    :param a: ranklist item
    :param b: ranklist item
    :return: bigger: -1, less: 1, equal 0
    '''

    if a['total_ac'] > b['total_ac']:
        return -1
    elif a['total_ac'] == b['total_ac']:
        if a['total_time'] < b['total_time']:
            return -1
        elif a['total_time'] == b['total_time']:
            return 0
        else:
            return 1
    else:
        return 1

def cmp_oirank(a,b):
    if a['total_score'] > b['total_score']:
        return -1
    if a['total_score'] == b['total_score']:
        return 0
    if a['total_score'] < b['total_score']:
        return 1

@contest.route('/balloon/<int:contest_id>', methods=['GET', 'POST'])
@login_required
def contest_show_balloon(contest_id):

    '''
        define operation of show balloons to be sent
    :param contest_id: contest_id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.manager_username != current_user.username and (current_user.is_admin() is False):
        abort(403)
    submissions = SubmissionStatus.query.filter_by(contest_id=contest_id, balloon_sent=False, status=current_app.config['LOCAL_SUBMISSION_STATUS']['Accepted']).order_by(SubmissionStatus.id.asc()).paginate(1, per_page=current_app.config['FLASKY_STATUS_PER_PAGE']).items
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    status_list = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    return render_template('contest/contest_balloon.html', submissions=submissions, contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end, contest_id=contest_id, status_list=status_list)


@contest.route('/balloon/<int:contest_id>/<int:run_id>', methods=['GET', 'POST'])
@login_required
def contest_sent_balloon(contest_id, run_id):

    '''
        define operation of sent balloons
    :param run_id: submission run id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.manager_username != current_user.username and (current_user.is_admin() is False):
        abort(403)
    submission = SubmissionStatus.query.get_or_404(run_id)
    submission.send_balloon()
    flash(u'已发送气球')
    return redirect(url_for('contest.contest_show_balloon', contest_id=contest_id))