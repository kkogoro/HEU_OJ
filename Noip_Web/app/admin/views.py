#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from .. import db
from ..models import Role, User, Permission, SchoolList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag, TagProblem, ContestUsers, ContestProblem, KeyValue, Blog, Challenge, ChallengeRound, ChallengeRoundProblem, ChallengeUserLevel, RoundUserLevel
from werkzeug.utils import secure_filename
from ..decorators import admin_required, permission_required
from datetime import datetime, timedelta
from .forms import ModifyProblem, ModifyTag, ModifyUser, ModifySchoolStatus, ModifySubmissionStatus, ModifyBlog, ModifyContest, AddContestProblem, ContestUserInsert, ModifySubmissionStatus4Noip, ModifyAnnounce, ModifyChallenge, ModifyChallengeRound
import os, base64, json

@admin.route('/')
@admin_required
def admin_index():

    '''
        deal with the index page of admin part
    :return: page
    '''

    # Todo: need to optimized the query
    user_num = User.query.count()
    unconfirmed_user = User.query.filter_by(confirmed=0).count()
    school_status = SchoolList.query.count()
    online_user_num = User.query.filter('last_seen>:last_seen').params(last_seen=datetime.utcnow()-timedelta(minutes=1)).count()
    problem_num = Problem.query.count()
    submission_num = SubmissionStatus.query.count()
    contest_num = Contest.query.count()
    tag_num = Tag.query.count()
    judging_num = SubmissionStatus.query.filter_by(status=current_app.config['LOCAL_SUBMISSION_STATUS']['Judging']).count()
    waiting_num = SubmissionStatus.query.filter_by(status=current_app.config['LOCAL_SUBMISSION_STATUS']['Waiting']).count()
    return render_template('admin/index.html', user_num=user_num, unconfirmed_user=unconfirmed_user, school_status=school_status, online_user_num=online_user_num, problem_num=problem_num, submission_num=submission_num, contest_num=contest_num, tag_num=tag_num, judging_num=judging_num, waiting_num=waiting_num)


@admin.route('/problems', methods=['GET', 'POST'])
@admin_required
def problem_list():

    '''
        deal with the problem list page of admin part
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Problem.query.order_by(Problem.id.asc()).paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    problems = pagination.items
    return render_template('admin/problem_list.html', problems=problems, pagination=pagination)


@admin.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
@admin_required
def problem_detail(problem_id):

    '''
        deal with the problem detail
    :param problem_id: problem id
    :return: page
    '''

    problem = Problem.query.get_or_404(problem_id)
    return render_template('admin/problem.html', problem=problem)


@admin.route('/problem/insert', methods=['GET', 'POST'])
@admin_required
def problem_insert():

    '''
        deal with the insert problem operation
    :return: page
    '''

    problem = Problem()
    form = ModifyProblem()
    if form.validate_on_submit():
        problem.school_id = form.school_id.data
        problem.title = form.title.data
        problem.time_limit = form.time_limit.data
        problem.memory_limit = form.memory_limit.data
        problem.special_judge = form.special_judge.data
        if form.type.data == 2:
            problem.type = True
        problem.submission_num = form.submission_num.data
        problem.accept_num = form.accept_num.data
        problem.description = form.description.data
        problem.input = form.input.data
        problem.output = form.output.data
        problem.sample_input = form.sample_input.data
        problem.sample_output = form.sample_output.data
        problem.source_name = form.source_name.data
        problem.hint = form.hint.data
        problem.author = form.author.data
        problem.visible = form.visible.data
        problem.last_update = datetime.utcnow()
        db.session.add(problem)
        db.session.commit()
        # add tags to the problem, delete old tags
        t = TagProblem.query.filter_by(problem_id=problem.id).all()
        for tag in t:
            db.session.delete(t)
        db.session.commit()
        for i in form.tags.data:
            t = TagProblem(tag_id=i, problem_id=problem.id)
            db.session.add(t)
            # db.session.commit()
        db.session.commit()
        current_user.log_operation('Insert problem "%s", problem_id is %s' % (problem.title, str(problem.id)))
        return redirect(url_for('admin.problem_list'))
    return render_template('admin/problem_insert.html', form=form, problem=problem)


@admin.route('/problem/edit/<int:problem_id>', methods=['GET', 'POST'])
@admin_required
def problem_edit(problem_id):

    '''
        deal with the edit problem operation
    :param problem_id: problem_id
    :return:
    '''

    problem = Problem.query.get_or_404(problem_id)
    form = ModifyProblem()
    if form.validate_on_submit():
        problem.school_id = form.school_id.data
        problem.title = form.title.data
        problem.time_limit = form.time_limit.data
        problem.memory_limit = form.memory_limit.data
        problem.special_judge = form.special_judge.data
        if form.type.data == 2:
            problem.type = True
        problem.submission_num = form.submission_num.data
        problem.accept_num = form.accept_num.data
        problem.description = form.description.data
        problem.input = form.input.data
        problem.output = form.output.data
        problem.sample_input = form.sample_input.data
        problem.sample_output = form.sample_output.data
        problem.source_name = form.source_name.data
        problem.hint = form.hint.data
        problem.author = form.author.data
        problem.visible = form.visible.data
        # add tags to the problem, delete old tags
        t = TagProblem.query.filter_by(problem_id=problem.id).all()
        for tag in t:
            db.session.delete(tag)
        db.session.commit()
        for i in form.tags.data:
            t = TagProblem(tag_id=i, problem_id=problem.id)
            db.session.add(t)
            # db.session.commit()
        problem.last_update = datetime.utcnow()
        db.session.add(problem)
        db.session.commit()
        current_user.log_operation('Edit problem "%s", problem_id is %s' % (problem.title, str(problem.id)))
        return redirect(url_for('admin.problem_list'))
    form.school_id.data = problem.school_id
    form.title.data = problem.title
    form.time_limit.data = problem.time_limit
    form.memory_limit.data = problem.memory_limit
    form.special_judge.data = problem.special_judge
    if problem.type:
        form.type.data = 2
    else:
        form.type.data = 1
    form.submission_num.data = problem.submission_num
    form.accept_num.data = problem.accept_num
    form.description.data = problem.description
    form.input.data = problem.input
    form.output.data = problem.output
    form.sample_input.data = problem.sample_input
    form.sample_output.data = problem.sample_output
    form.source_name.data = problem.source_name
    form.hint.data = problem.hint
    form.author.data = problem.author
    form.visible.data = problem.visible
    form.tags.data = problem.tags
    return render_template('admin/problem_edit.html', form=form, problem=problem)


@admin.route('/upload/<int:problem_id>', methods=['GET', 'POST'])
@admin_required
def upload_file(problem_id):

    '''
        deal with the input file list upload operation
    :param problem_id: problem_id
    :return: None
    '''

    problem = Problem.query.get_or_404(problem_id)
    if request.method == 'POST':
        if not os.path.exists(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/'):
            os.makedirs(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/')
        for f in request.files.getlist('file'):
            # print os.path.join(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/', f.filename)
            f.save(os.path.join(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/', f.filename))
    return render_template('admin/upload.html', problem_id=problem_id)


@admin.route('/tags', methods=['GET', 'POST'])
@admin_required
def tag_list():

    '''
        define tag list operations
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.order_by(Tag.id.desc()).paginate(page, per_page=current_app.config['FLASKY_TAGS_PER_PAGE'])
    tags = pagination.items
    return render_template('admin/tag_list.html', tags=tags,  pagination=pagination)


@admin.route('/tag/edit/<int:tag_id>', methods=['GET', 'POST'])
@admin_required
def tag_edit(tag_id):

    '''
        define edit tag operation
    :param tag_id: tag id
    :return: page
    '''

    tag = Tag.query.get_or_404(tag_id)
    form = ModifyTag()
    if form .validate_on_submit():
        tag.tag_name = form.tag_name.data
        db.session.add(tag)
        db.session.commit()
        current_user.log_operation('Edit tag %s, tag_id is %s' % (tag.tag_name, str(tag.id)))
        flash('Tag update sucessful!')
        return redirect(url_for('admin.tag_list'))
    form.tag_name.data = tag.tag_name
    return render_template('admin/tag_edit.html', form=form)


@admin.route('/tag/add', methods=['GET', 'POST'])
@admin_required
def tag_insert():

    '''
        define add tag operation
    :return: page
    '''

    tag = Tag()
    form = ModifyTag()
    if form.validate_on_submit():
        tag.tag_name = form.tag_name.data
        db.session.add(tag)
        db.session.commit()
        current_user.log_operation('Add tag %s' % tag.tag_name)
        flash('Add tag sucessful!')
        return redirect(url_for('admin.tag_list'))
    form.tag_name.data = ''
    return render_template('admin/tag_edit.html', form=form)


@admin.route('/users', methods=['GET', 'POST'])
@admin_required
def user_list():

    '''
        deal with user list operation
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.asc()).paginate(page, per_page=current_app.config['FLASKY_USERS_PER_PAGE'])
    users = pagination.items
    return render_template('admin/user_list.html', users=users, pagination=pagination)


@admin.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):

    '''
        deal with user edit operation
    :param user_id: user_id
    :return: page
    '''

    user = User.query.get_or_404(user_id)
    form = ModifyUser(user)
    if form.validate_on_submit():
        # if user.role.permission >= current_user.role.permission and current_user.username != user.username and current_user.role.permission != 0xff:
        #     current_user.log_operation(
        #         'Try to edit a high level permission user %s, user_id is %s' % (user.username, str(user.id)))
        #     flash(u"您无法编辑一个更高权限的用户!")
        #     return redirect(url_for('admin.user_list'))
        # if change to a high level role, the operation can not be exec
        # elif Role.query.get_or_404(form.role_id.data).permission >= current_user.role.permission and current_user.role.permission != 0xff:
        #     current_user.log_operation(
        #         'Try to grant user %s a high level permission, user_id is %s' % (user.username, str(user.id)))
        #     flash(u"您不能给用户授予高于您本身的权限!")
        #     return redirect(url_for('admin.user_edit', user_id=user_id))
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.nickname = form.nickname.data
        user.gender = form.gender.data
        user.major = form.major.data
        user.degree = form.degree.data
        user.current_level = form.challenge_level.data
        user.country = form.country.data
        user.address = form.address.data
        user.school_id = form.school_id.data
        user.student_num = form.student_num.data
        user.phone_num = form.phone_num.data
        user.about_me = form.about_me.data
        user.role_id = form.role_id.data
        if form.password.data != '' and form.password.data is not None:
            user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        current_user.log_operation('Edit user %s, user_id is %s' % (user.username, str(user.id)))
        flash('Update successful!')
        return redirect(url_for('admin.user_list'))
    form.email.data = user.email
    form.username.data = user.username
    form.nickname.data = user.nickname
    form.confirmed.data = user.confirmed
    form.role_id.data = user.role_id
    form.challenge_level.data = user.current_level
    form.gender.data = user.gender
    form.major.data = user.major
    form.degree.data = user.degree
    form.address.data = user.address
    form.country.data = user.country
    form.school_id.data = user.school_id
    form.student_num.data = user.student_num
    form.phone_num.data = user.phone_num
    form.about_me.data = user.about_me
    return render_template('admin/user_edit.html', form=form, user=user)


@admin.route('/user/<username>', methods=['GET', 'POST'])
@admin_required
def user_detail(username):

    '''
        define user detail operation
    :param username: username
    :return: page
    '''

    user = User.query.filter_by(username=username).first_or_404()
    return render_template('admin/user_detail.html', user=user)


@admin.route('/school-status', methods=['GET', 'POST'])
@admin_required
def school_list():

    '''
        define operations about showing school list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = SchoolList.query.order_by(SchoolList.id.asc()).paginate(page, per_page=current_app.config['FLASKY_OJS_PER_PAGE'])
    school = pagination.items
    return render_template('admin/school_list.html', school=school, pagination=pagination)


@admin.route('/school-status/<int:school_id>', methods=['GET', 'POST'])
@admin_required
def school_status(school_id):

    '''
        define operations about showing school status
    :param school_id: school_id
    :return: page
    '''

    school = SchoolList.query.get_or_404(school_id)
    return render_template('admin/school_detail.html', school=school)


@admin.route('/school-status/edit/<int:school_id>', methods=['GET', 'POST'])
@admin_required
def school_status_edit(school_id):

    '''
        define operations about editing school status
    :param school_id: school_id
    :return: page
    '''

    school = SchoolList.query.get_or_404(school_id)
    form = ModifySchoolStatus()
    if form.validate_on_submit():
        school.school_name = form.school_name.data
        school.description = form.description.data
        db.session.add(school)
        db.session.commit()
        current_user.log_operation('Edit school %s Status, school_id is %s' % (school.school_name, str(school.id)))
        flash('Update school status successful!')
        return redirect(url_for('admin.school_list'))
    form.school_name.data = school.school_name
    form.description.data = school.description
    return render_template('admin/school-status_edit.html', form=form, school=school)


@admin.route('/school-status/add', methods=['GET', 'POST'])
@admin_required
def school_status_insert():

    '''
        define operations about adding school status
    :return: page
    '''

    school = SchoolList()
    form = ModifySchoolStatus()
    if form.validate_on_submit():
        school.school_name = form.school_name.data
        school.description = form.description.data
        db.session.add(school)
        db.session.commit()
        current_user.log_operation('Add school %s, school_id is %s' % (school.school_name, str(school.id)))
        flash('Add school status successful!')
        return redirect(url_for('admin.school_list'))
    return render_template('admin/school-status_add.html', form=form)


@admin.route('/school-status/delete', methods=['GET', 'POST'])
@admin_required
def school_status_delete():

    '''
        define operations about deleting school status
    :return: page
    '''

    # get school_id from GET request
    school_id = request.args.get('school_id', -1, type=int)
    if school_id != -1:
        school = SchoolList.query.get(school_id)
        if school is not None:
            db.session.delete(school)
            db.session.commit()
            current_user.log_operation('Delete school %s, school_id is %s' % (school.school_name, str(school.id)))
            flash('Delete school successful!')
            return redirect(url_for('admin.school_list'))
        else:
            flash('No such school in school_list!')
    else:
        flash('No such school in school_list!')
    return redirect(url_for('admin.school_list'))


@admin.route('/submission-status', methods=['GET', 'POST'])
@admin_required
def submission_status_list():

    '''
        define operations about showing submission status
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = SubmissionStatus.query.order_by(SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    status = pagination.items
    submissions = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        submissions[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    return render_template('admin/submission_status_list.html', submissions=submissions, language=language, status=status, pagination=pagination)


@admin.route('/submission-status/<int:submission_id>', methods=['GET', 'POST'])
@admin_required
def submission_status_detail(submission_id):

    '''
        define submission status showing page
    :param submission_id: submission_id
    :return: page
    '''

    status_detail = SubmissionStatus.query.filter_by(id=submission_id).first_or_404()
    if status_detail==None or status_detail==() or status_detail==[]:
        print("error in status_detail !")
    code = base64.b64decode(status_detail.code).decode('utf-8')
    ce_info = CompileInfo.query.filter_by(submission_id=submission_id).first()
    submissions = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        submissions[str(current_app.config['LOCAL_SUBMISSION_STATUS'][k])] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    status_sub = []

    if status_detail.problem.type == True and status_detail.status >= 0:
        try:
            sub = status_detail.child_status.split(';')
            for i in sub:
                status_sub.append(i.split(','))
        except ValueError, e:
            print "Value error in status %d child_status" % status_detail.id

    return render_template('admin/submission_status_detail.html', submissions=submissions, language=language, status=status_detail, code=code, ce_info=ce_info, status_sub=status_sub)


@admin.route('/submission-status/edit/<int:submission_id>', methods=['GET', 'POST'])
@admin_required
def submission_status_edit(submission_id):

    '''
        define operations about editing submission status
    :param submission_id: submission_id
    :return: page
    '''

    status_detail = SubmissionStatus.query.filter_by(id=submission_id).first_or_404()
    code = base64.b64decode(status_detail.code)
    ce_info = CompileInfo.query.filter_by(submission_id=submission_id).first()
    if status_detail.problem.type is True:
        form = ModifySubmissionStatus4Noip()
        if form.validate_on_submit():
            status_detail.status = form.status.data
            status_detail.child_status = form.exec_sub.data
            status_detail.visible = form.visible.data
            db.session.add(status_detail)
            db.session.commit()
            if status_detail.status == 100:
                problem = Problem.query.with_lockmode('update').get(status_detail.problem_id)
                problem.accept_num = problem.accept_num + 1
                db.session.add(problem)
                db.session.commit()
                if status_detail.challenge_round is not None:
                    if SubmissionStatus.query.filter_by(problem_id=status_detail.problem_id, status=100).count() == 1:
                        round_user = RoundUserLevel.query.with_lockmode('update').get((status_detail.author.id, status_detail.challenge_round.id))
                        if round_user is None:
                            round_user = RoundUserLevel(user_id=status_detail.author.id, round_id=status_detail.challenge_round.id, problem_pass=0)
                        round_user.problem_pass = round_user.problem_pass + 1
                        if round_user.problem_pass == status_detail.challenge_round.problems.count():
                            challenge_user = ChallengeUserLevel.query.with_lockmode('update').get((status_detail.author.id, status_detail.challenge_round.challenge_id))
                            if challenge_user is None:
                                challenge_user = ChallengeUserLevel(user_id=status_detail.author.id, challenge_id=status_detail.challenge_round.challenge_id, round_pass=0)
                            challenge_user.round_pass = challenge_user.round_pass + 1
                        db.session.add(round_user)
                        db.session.add(challenge_user)
                        db.session.commit()
                        if challenge_user.round_pass == status_detail.challenge_round.query.filter_by(challenge_id=status_detail.challenge_id).count():
                            current_user.current_level = current_user.current_level + 1
                            db.session.add(current_user)
                            db.session.commit()
            return redirect(url_for('admin.submission_status_list'))
        form.status.data = status_detail.status
        form.exec_sub.data = status_detail.child_status
        form.visible.data = status_detail.visible
        return render_template('admin/submission_edit_status4noip.html', status=status_detail, code=code, ce_info=ce_info,
                               form=form)
    else:
        form = ModifySubmissionStatus()
        if form.validate_on_submit():
            status_detail.status = form.status.data
            status_detail.exec_time = form.exec_time.data
            status_detail.exec_memory = form.exec_memory.data
            status_detail.visible = form.visible.data
            db.session.add(status_detail)
            db.session.commit()
            if status_detail.status == -1:
                problem = Problem.query.with_lockmode('update').get(status_detail.problem_id)
                problem.accept_num = problem.accept_num + 1
                db.session.add(problem)
                db.session.commit()
                if status_detail.challenge_round is not None:
                    if SubmissionStatus.query.filter_by(problem_id=status_detail.problem_id, status=-1).count() == 1:
                        round_user = RoundUserLevel.query.with_lockmode('update').get(
                            (status_detail.author.id, status_detail.challenge_round.id))
                        if round_user is None:
                            round_user = RoundUserLevel(user_id=status_detail.author.id, round_id=status_detail.challenge_round.id, problem_pass=0)
                        round_user.problem_pass = round_user.problem_pass + 1
                        if round_user.problem_pass == status_detail.challenge_round.problems.count():
                            challenge_user = ChallengeUserLevel.query.with_lockmode('update').get((status_detail.author.id, status_detail.challenge_round.challenge_id))
                            if challenge_user is None:
                                challenge_user = ChallengeUserLevel(user_id=status_detail.author.id, challenge_id=status_detail.challenge_round.challenge_id, round_pass=0)
                            challenge_user.round_pass = challenge_user.round_pass + 1
                        db.session.add(round_user)
                        db.session.add(challenge_user)
                        db.session.commit()
                        if challenge_user.round_pass == status_detail.challenge_round.query.filter_by(challenge_id=status_detail.challenge_id).count():
                            current_user.current_level = current_user.current_level + 1
                            db.session.add(current_user)
                            db.session.commit()
            return redirect(url_for('admin.submission_status_list'))
        form.status.data = status_detail.status
        form.exec_time.data = status_detail.exec_time
        form.exec_memory.data = status_detail.exec_memory
        form.visible.data = status_detail.visible
        return render_template('admin/submission_edit_status.html', status=status_detail, code=code, ce_info=ce_info, form=form)


@admin.route('/logs', methods=['GET', 'POST'])
@admin_required
def log_list():

    '''
        define operations about showing website log
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Logs.query.order_by(Logs.id.desc()).paginate(page, per_page=current_app.config['FLASKY_LOGS_PER_PAGE'])
    logs = pagination.items
    return render_template('admin/log_list.html', logs=logs, pagination=pagination)


@admin.route('/blogs', methods=['GET', 'POST'])
@admin_required
def blog_list():

    '''
        define operations about showing blog
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(Blog.id.desc()).paginate(page, per_page=current_app.config['FLASKY_BLOGS_PER_PAGE'])
    blogs = pagination.items
    return render_template('admin/blog_list.html', blogs=blogs, pagination=pagination)


@admin.route('/blog/add', methods=['GET', 'POST'])
@admin_required
def blog_insert():

    '''
        define operation about insert blog
    :return: page
    '''

    blog = Blog()
    form = ModifyBlog()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        blog.author_username = current_user.username
        blog.public = form.public.data
        db.session.add(blog)
        db.session.commit()
        current_user.log_operation('Add blog %s, blog_id is %s' % (blog.title, str(blog.id)))
        flash('Add blog successful!')
        return redirect(url_for('admin.blog_list'))
    return render_template('admin/blog_add.html', form=form)


@admin.route('/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
@admin_required
def blog_edit(blog_id):

    '''
        define operation about edit blog
    :return: page
    '''

    blog = Blog.query.get_or_404(blog_id)
    form = ModifyBlog()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        blog.author_username = current_user.username
        blog.public = form.public.data
        blog.last_update = datetime.utcnow()
        db.session.add(blog)
        db.session.commit()
        current_user.log_operation('Edit blog %s, blog_id is %s' % (blog.title, str(blog.id)))
        flash('Edit blog successful!')
        return redirect(url_for('admin.blog_list'))
    form.title.data = blog.title
    form.content.data = blog.content
    form.public.data = blog.public
    return render_template('admin/blog_edit.html', form=form)


@admin.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
@admin_required
def blog_detail(blog_id):

    '''
        define operation about blog detail
    :param blog_id: blog_id
    :return: page
    '''

    blog = Blog.query.get_or_404(blog_id)
    return render_template('admin/blog_detail.html', blog=blog)

@admin.route('/contests', methods=['GET', 'POST'])
@admin_required
def contest_list():

    '''
        define show contest list operation
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Contest.query.order_by(Contest.id.desc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    contests = pagination.items
    now = datetime.utcnow()
    return render_template('admin/contest_list.html', contests=contests, pagination=pagination, now=now)


@admin.route('/contest/<int:contest_id>', methods=['GET', 'POST'])
@admin_required
def contest_detail(contest_id):

    '''
        define operations about contest
    :param contest_id: contest id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    return render_template('admin/contest_detail.html', contest=contest)


@admin.route('/contest/add', methods=['GET', 'POST'])
@admin_required
def contest_insert():
    contest = Contest()
    form = ModifyContest()
    if form.validate_on_submit():
        contest.contest_name = form.contest_name.data
        contest.school_id = form.school_id.data
        contest.start_time = form.start_time.data - timedelta(hours=8)
        contest.end_time = form.end_time.data - timedelta(hours=8)
        contest.type = form.rule.data - 1
        # end_time is smaller than start_time, we use the 5 hours later time as the end time
        if contest.end_time <= contest.start_time:
            contest.end_time = contest.start_time + timedelta(hours=5)
        # Five types contest
        if form.type.data == 1:
            # contest we need to registe, no password, no verify
            contest.style = 1
            contest.verify = False
            contest.password = ''
        elif form.type.data == 2 or form.type.data == 4:
            # contest we need to registe or pre register of onsite contest, no password, but has verify by the manager
            contest.style = form.type.data
            contest.verify = True
            contest.password = ''
        elif form.type.data == 3:
            # contest we need to registe, has the password, no verify
            contest.style = 3
            contest.verify = False
            contest.password = form.password.data
            if form.password.data == '':
                flash(u'密码保护的比赛密码不能为空!')
                return redirect(url_for('admin.contest_insert', contest_id=contest.id))
        elif form.type.data == 5:
            # contest onsite, no password, no verify
            contest.style = 5
            contest.verify = False
            contest.password = ''
        contest.description = form.description.data
        contest.announce = form.announce.data
        contest.visible = form.visible.data
        contest.manager_username = form.manager.data
        contest.rank_frozen = form.rank_frozen.data
        db.session.add(contest)
        db.session.commit()
        current_user.log_operation('Add contest %s, contest_id is %s' % (contest.contest_name, str(contest.id)))
        flash(u'添加比赛成功!')
        # Todo: check if the contest.id is good for use
        return redirect(url_for('admin.add_contest_problem', contest_id=contest.id))
    form.contest_name.data = contest.contest_name
    form.school_id.data = contest.school_id
    form.start_time.data = contest.start_time
    form.end_time.data = contest.end_time
    form.type.data = contest.style
    form.password.data = contest.password
    form.description.data = contest.description
    form.announce.data = contest.announce
    form.visible.data = contest.visible
    form.manager.data = contest.manager_username
    form.rank_frozen.data = contest.rank_frozen
    return render_template('admin/contest_add.html', form=form, contest=contest, current_time=datetime.utcnow())


@admin.route('/contest/edit/<int:contest_id>', methods=['GET', 'POST'])
@admin_required
def contest_edit(contest_id):

    '''
        define edit contest operation
    :param contest_id: contest_id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    form = ModifyContest()
    form.rule.data = int(contest.type) + 1
    if form.validate_on_submit():
        contest.contest_name = form.contest_name.data
        contest.school_id = form.school_id.data
        contest.start_time = form.start_time.data - timedelta(hours=8)
        contest.end_time = form.end_time.data - timedelta(hours=8)
        # end_time is smaller than start_time, we use the 5 hours later time as the end time
        if contest.end_time <= contest.start_time:
            contest.end_time = contest.start_time + timedelta(hours=5)
        # Five types contest
        if form.type.data == 1:
            # contest we need to registe, no password, no verify
            contest.style = 1
            contest.verify = False
            contest.password = ''
        elif form.type.data == 2 or form.type.data == 4:
            # contest we need to registe or pre register of onsite contest, no password, but has verify by the manager
            contest.style = form.type.data
            contest.verify = True
            contest.password = ''
        elif form.type.data == 3:
            # contest we need to registe, has the password, no verify
            contest.style = 3
            contest.verify = False
            contest.password = form.password.data
            if form.password.data == '':
                flash(u'密码保护的比赛密码不能为空!')
                return redirect(url_for('admin.contest_insert', contest_id=contest.id))
        elif form.type.data == 5:
            # contest onsite, no password, no verify
            contest.style = 5
            contest.verify = False
            contest.password = ''
        contest.description = form.description.data
        contest.announce = form.announce.data
        contest.visible = form.visible.data
        contest.manager_username = form.manager.data
        contest.rank_frozen = form.rank_frozen.data
        db.session.add(contest)
        db.session.commit()
        current_user.log_operation('Edit contest %s, contest_id is %s' % (contest.contest_name, str(contest.id)))
        flash(u'编辑比赛成功!')
        # Todo: check if the contest.id is good for use
        return redirect(url_for('admin.add_contest_problem', contest_id=contest.id))
    form.contest_name.data = contest.contest_name
    form.school_id.data = contest.school_id
    form.rule.data = int(contest.type) + 1
    form.start_time.data = contest.start_time + timedelta(hours=8)
    form.end_time.data = contest.end_time + timedelta(hours=8)
    form.type.data = contest.style
    form.password.data = contest.password
    form.description.data = contest.description
    form.announce.data = contest.announce
    form.visible.data = contest.visible
    form.manager.data = contest.manager_username
    form.rank_frozen.data = contest.rank_frozen
    return render_template('admin/contest_edit.html', form=form, contest=contest, current_time=datetime.utcnow())


@admin.route('/contest/edit/add_problem/<int:contest_id>', methods=['GET', 'POST'])
@admin_required
def add_contest_problem(contest_id):

    '''
        define contest add problem operation
    :param contest_id: contest id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    form = AddContestProblem()
    if form.validate_on_submit():
        problem = Problem.query.get(form.problem_id.data)
        if problem is not None:
            if ContestProblem.query.filter_by(problem_id=problem.id, contest_id=contest_id).first() != None:
                flash(u'题目已添加至比赛中，请勿重复添加!')
                return redirect(url_for('admin.add_contest_problem', contest_id=contest_id))
            if problem.type != contest.type :
                if contest.type :
                    flash(u'OI比赛不能添加ACM规则试题!')
                    return redirect(url_for('admin.add_contest_problem', contest_id=contest_id))
                else :
                    flash(u'ACM比赛不能添加OI规则试题!')
                    return redirect(url_for('admin.add_contest_problem', contest_id=contest_id))
            contest_problem = ContestProblem(contest=contest, problem=problem)
            contest_problem.problem_index = contest.problems.count() + 1000
            if form.problem_alias.data != '' and form.problem_alias.data is not None:
                contest_problem.problem_alias = form.problem_alias.data
            else:
                contest_problem.problem_alias = problem.title
            db.session.add(contest_problem)
            db.session.commit()
            current_user.log_operation('Add problem %s to contest %s, problem id is %s, contest_id is %s' % (problem.title, contest.contest_name, str(problem.id), str(contest.id)))
            flash(u'添加题目成功!')
            return redirect(url_for('admin.add_contest_problem', contest_id=contest.id))
        else:
            flash(u'题目不存在!')
    return render_template('admin/contest_add_problem.html', form=form, contest=contest)


@admin.route('/contest/edit/delete_problem/<int:contest_id>', methods=['GET', 'POST'])
@admin_required
def delete_contest_problem(contest_id):

    '''
        define contest delete problem operation
    :param contest_id: contest_id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    # get problem_id from GET request
    problem_id = request.args.get('problem_id', -1, type=int)
    # if we get a problem id
    if problem_id != -1:
        # try to get the problem
        problem = Problem.query.get(problem_id)
        # the problem id is valid
        if problem is not None:
            # get the contest_problem data from the sql
            contest_problem = contest.problems.filter_by(problem_id=problem.id).first()
            # problem is in the contest
            if contest_problem:
                # delete it
                db.session.delete(contest_problem)
                db.session.commit()
                current_user.log_operation('Delete problem %s from contest %s, problem id is %s, contest_id is %s' % (problem.title, contest.contest_name, str(problem.id), str(contest.id)))
                flash(u'删除成功')
            else:
                flash(u'比赛题目列表中没有该题目！')
        else:
            flash(u'题目列表中不存在该题目！')
    else:
        flash(u'请指定题目ID')
    return redirect(url_for('admin.add_contest_problem', contest_id=contest_id))


@admin.route('/contest/edit/rejudge/<int:contest_id>', methods=['GET', 'POST'])
@admin_required
def rejudge_contest_problem(contest_id):

    '''
        define operation about rejudge contest problem
    :param contest_id: contest_id
    :return: redirect
    '''

    contest = Contest.query.get_or_404(contest_id)
    # get problem_id from GET request
    problem_id = request.args.get('problem_id', -1, type=int)
    # if we get a problem id
    if problem_id != -1:
        # try to get the problem
        problem = Problem.query.get(problem_id)
        # the problem id is valid
        if problem is not None:
                # rejudge it
            submissions = contest.submissions.filter_by(problem_id=problem.id).all()
            for item in submissions:
                item.status = -100
                db.session.add(item)
            db.session.commit()
            current_user.log_operation('Rejudge problem %s from contest %s, problem id is %s, contest_id is %s' % (
            problem.title, contest.contest_name, str(problem.id), str(contest.id)))
            flash(u'rejudge请求提交成功')
        else:
            flash(u'题目列表中不存在该题目！')
    else:
        flash(u'请指定题目ID')
    return redirect(url_for('admin.contest_detail', contest_id=contest_id))


@admin.route('/contest/insert_user/<int:contest_id>', methods=['GET', 'POST'])
@admin_required
def contest_insert_user(contest_id):

    '''
        define operation about insert user into contest
    :param contest_id: contest_id
    :return: page
    '''

    '''
        users = ["user_realname, student_num, school_id, phone_num, username, password, email", ....]
        用户名和密码不能跨网站更新,当前用户名和邮箱冲突的话会强制更新用户名的邮箱
    '''
    contest = Contest.query.get_or_404(contest_id)
    form = ContestUserInsert()
    if form.validate_on_submit():
        users = form.user_list.data.strip().split(';')
        user_to_insert = []
        for user in users:
            user = user.strip()
            user_detail = user.split(',')
            if len(user_detail) != 7:
                flash(u'输入的用户数据错误, 每个数据行只能有7个元素,数据行间以英文分号分隔!')
                return redirect(url_for('admin.contest_insert_user',contest_id=contest_id))
            find_user = User.query.filter_by(username=user_detail[4].strip()).first()
            if find_user is not None:
                find_user.realname = user_detail[0].strip()
                find_user.student_num = user_detail[1].strip()
                find_user.school_id = user_detail[2].strip()
                find_user.phone_num = user_detail[3].strip()
                find_user.password = user_detail[5].strip()
                find_user.email = user_detail[6].strip()
                find_user.confirmed = True
            else:
                find_user = User()
                find_user.username = user_detail[4].strip()
                find_user.realname = user_detail[0].strip()
                find_user.nickname = user_detail[0].strip()
                find_user.student_num = user_detail[1].strip()
                find_user.school_id = user_detail[2].strip()
                find_user.phone_num = user_detail[3].strip()
                find_user.password = user_detail[5].strip()
                find_user.email = user_detail[6].strip()
                find_user.confirmed = True
            user_to_insert.append(find_user)
        for user in user_to_insert:
            db.session.add(user)
            db.session.commit()
            contest_user = ContestUsers(
                user_id=user.id,
                contest_id=contest_id,
                realname=user.realname,
                address=user.address,
                school_id=user.school_id,
                student_num=user.student_num,
                phone_num=user.phone_num,
                user_confirmed=True,
                register_time=datetime.utcnow()
            )
            db.session.add(contest_user)
            db.session.commit()
        flash(u'插入用户成功!')
        return redirect(url_for('admin.contest_detail', contest_id=contest_id))
    return render_template('admin/contest_insert_user.html', form=form, contest=contest)


@admin.route('/announce/edit', methods=['GET', 'POST'])
@admin_required
def modify_announce():

    '''
        define modify_announcement
    :return: page
    '''

    form = ModifyAnnounce()
    announce_id = KeyValue.query.filter_by(key='announce_id').first()
    if form.validate_on_submit():
        blog = Blog.query.get(form.blog_id.data)
        if form.blog_id.data != 0 and blog is None:
            flash(u'Blog不存在!')
            return render_template('admin/announce_modify.html', form=form)
        elif form.blog_id.data != 0 and blog.public is False:
            flash(u'Blog不可见!请先把Blog设置为可见！')
            return render_template('admin/announce_modify.html', form=form)
        else:
            if announce_id is None:
                announce_id = KeyValue(key='announce_id')
            announce_id.value = form.blog_id.data
            db.session.add(announce_id)
            db.session.commit()
            current_user.log_operation('Modify announce to blog %s' % (form.blog_id.data))
            flash(u'编辑通知成功!')
            return redirect(url_for('admin.modify_announce'))
    if announce_id is None or int(announce_id.value) == 0:
        form.blog_id.data = 0
    else:
        form.blog_id.data = announce_id.value
    return render_template('admin/announce_modify.html', form=form)


@admin.route('/challenge', methods=['GET', 'POST'])
@admin_required
def challenge_list():

    '''
        define challenge_list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Challenge.query.order_by(Challenge.challenge_level.asc()).paginate(page, per_page=current_app.config['FLASKY_USERS_PER_PAGE'])
    challenge = pagination.items
    return render_template('admin/challenge_list.html', challenge=challenge, pagination=pagination)

@admin.route('/challenge/<int:challenge_id>/edit/', methods=['GET', 'POST'])
@admin_required
def edit_challenge(challenge_id):

    '''
        define edit challenge_func
    :param challenge_id: challenge_id
    :return: page
    '''

    challenge = Challenge.query.get_or_404(challenge_id)
    form = ModifyChallenge()
    if form.validate_on_submit():
        challenge.challenge_level = form.challenge_level.data
        challenge.challenge_name = form.challenge_name.data
        db.session.add(challenge)
        db.session.commit()
        flash(u'挑战编辑成功')
        return redirect(url_for('admin.challenge_list'))
    form.challenge_level.data = challenge.challenge_level
    form.challenge_name.data = challenge.challenge_name
    return render_template('admin/challenge_edit.html', form=form)


@admin.route('/challenge/insert', methods=['GET', 'POST'])
@admin_required
def insert_challenge():

    '''
        define insert challenge_func
    :return: page
    '''

    challenge = Challenge()
    form = ModifyChallenge()
    if form.validate_on_submit():
        challenge.challenge_level = form.challenge_level.data
        challenge.challenge_name = form.challenge_name.data
        db.session.add(challenge)
        db.session.commit()
        flash(u'挑战添加成功')
        return redirect(url_for('admin.challenge_list'))
    return render_template('admin/challenge_edit.html', form=form)


@admin.route('/challenge/<int:challenge_id>/round', methods=['GET', 'POST'])
@admin_required
def challenge_round_list(challenge_id):

    '''
        define challenge round list
    :param challenge_id: challeng_id
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    challenge = Challenge.query.get_or_404(challenge_id)
    pagination = challenge.challenge_round.order_by(ChallengeRound.id.asc()).paginate(page, per_page=current_app.config['FLASKY_USERS_PER_PAGE'])
    round = pagination.items
    return render_template('admin/challenge_round_list.html', round=round, challenge=challenge,  pagination=pagination)

@admin.route('/challenge/round/insert', methods=['GET', 'POST'])
@admin_required
def insert_challenge_round():

    '''
        define challenge round insert
    :return: page
    '''

    form = ModifyChallengeRound()
    if form.validate_on_submit():
        challenge = Challenge.query.get(form.challenge_id.data)
        if challenge is None:
            flash(u'挑战不存在！')
            return redirect(url_for('admin.insert_challenge_round'))
        round = ChallengeRound()
        round.round_name = form.round_name.data
        round.challenge_id = form.challenge_id.data
        db.session.add(round)
        db.session.commit()
        flash(u'关卡添加成功')
        return redirect(url_for('admin.challenge_round_list', challenge_id=form.challenge_id.data))
    return render_template('admin/challenge_round_insert.html', form=form)


@admin.route('/challenge/round/<int:round_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_challenge_round(round_id):

    '''
        define challend round edit
    :param round_id: round
    :return: page
    '''

    round = ChallengeRound.query.get_or_404(round_id)
    form = ModifyChallengeRound()
    if form.validate_on_submit():
        challenge = Challenge.query.get(form.challenge_id.data)
        if challenge is None:
            flash(u'挑战不存在！')
            return redirect(url_for('admin.insert_challenge_round'))
        round.round_name = form.round_name.data
        round.challenge_id = form.challenge_id.data
        db.session.add(round)
        db.session.commit()
        flash(u'关卡编辑成功')
        return redirect(url_for('admin.challenge_round_list', challenge_id=form.challenge_id.data))
    form.round_name.data = round.round_name
    form.challenge_id.data = round.challenge_id
    return render_template('admin/challenge_round_edit.html', form=form)


@admin.route('/challenge/round/<int:round_id>/edit/add_problem', methods=['GET', 'POST'])
@admin_required
def add_round_problem(round_id):

    '''
        define round add problem operation
    :param round_id: round_id id
    :return: page
    '''

    round = ChallengeRound.query.get_or_404(round_id)
    form = AddContestProblem()
    if form.validate_on_submit():
        problem = Problem.query.get(form.problem_id.data)
        if problem is not None:
            if ChallengeRoundProblem.query.filter_by(problem_id=problem.id, round_id=round_id).first() != None:
                flash(u'题目已添加至关卡中，请勿重复添加!')
                return redirect(url_for('admin.add_round_problem', round_id=round_id))
            elif problem.school_id != 1:
                flash(u'题目不属于公共题库，不允许添加！')
                return redirect(url_for('admin.add_round_problem', round_id=round_id))
            round_problem = ChallengeRoundProblem(challenge_round=round, problem=problem)
            round_problem.problem_index = round.problems.count() + 1000
            if form.problem_alias.data != '' and form.problem_alias.data is not None:
                round_problem.problem_alias = form.problem_alias.data
            else:
                round_problem.problem_alias = problem.title
            db.session.add(round_problem)
            db.session.commit()
            current_user.log_operation('Add problem %s to round %s, problem id is %s, round_id is %s' % (problem.title, round.round_name, str(problem.id), str(round.id)))
            flash(u'添加题目成功!')
        else:
            flash(u'题目不存在!')
    return render_template('admin/challenge_round_add_problem.html', form=form, round=round)


@admin.route('/challenge/round/<int:round_id>/edit/delete_problem', methods=['GET', 'POST'])
@admin_required
def delete_round_problem(round_id):

    '''
        define contest delete round operation
    :param round_id: round_id
    :return: page
    '''

    round = ChallengeRound.query.get_or_404(round_id)
    # get problem_id from GET request
    problem_id = request.args.get('problem_id', -1, type=int)
    # if we get a problem id
    if problem_id != -1:
        # try to get the problem
        problem = Problem.query.get(problem_id)
        # the problem id is valid
        if problem is not None:
            # get the contest_problem data from the sql
            round_problem = round.problems.filter_by(problem_id=problem.id).first()
            # problem is in the contest
            if round_problem:
                # delete it
                db.session.delete(round_problem)
                db.session.commit()
                current_user.log_operation('Delete problem %s from round %s, problem id is %s, round_id is %s' % (problem.title, round.round_name, str(problem.id), str(round.id)))
                flash(u'删除成功')
            else:
                flash(u'关卡题目列表中没有该题目！')
        else:
            flash(u'题目列表中不存在该题目！')
    else:
        flash(u'请指定题目ID')
    return redirect(url_for('admin.add_round_problem', round_id=round_id))


@admin.route('/challenge/round/<int:round_id>/edit/rejudge', methods=['GET', 'POST'])
@admin_required
def rejudge_round_problem(round_id):

    '''
        define operation about rejudge round problem
    :param round_id: round_id
    :return: redirect
    '''

    round = ChallengeRound.query.get_or_404(round_id)
    # get problem_id from GET request
    problem_id = request.args.get('problem_id', -1, type=int)
    # if we get a problem id
    if problem_id != -1:
        # try to get the problem
        problem = Problem.query.get(problem_id)
        # the problem id is valid
        if problem is not None:
                # rejudge it
            submissions = round.submissions.filter_by(problem_id=problem.id).all()
            for item in submissions:
                item.status = -100
                db.session.add(item)
            db.session.commit()
            current_user.log_operation('Rejudge problem %s from round %s, problem id is %s, round_id is %s' % (
            problem.title, round.contest_name, str(problem.id), str(round.id)))
            flash(u'rejudge请求提交成功')
        else:
            flash(u'题目列表中不存在该题目！')
    else:
        flash(u'请指定题目ID')
    return redirect(url_for('admin.contest_detail', round_id=round_id))

#
# import pickle
#
#
# @admin.route('/functions', methods=['GET', 'POST'])
# @admin_required
# def functions_management():
#     '''
#         define operation about rejudge round problem
#     :param round_id: round_id
#     :return: redirect
#     '''
#     func = KeyValue.query.filter_by(key="functions_open").first()
#     if func is not None:
#         value = pickle.load(func.value)
#
#     else:
#
#     return redirect(url_for('admin.contest_detail', round_id=round_id))
#
