#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField, IntegerField, SelectMultipleField, DateTimeField, FloatField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, InputRequired
from wtforms import validators, ValidationError
from ..models import Role, User, Permission, SchoolList, Tag, Contest, Challenge
from flask import current_app
from datetime import datetime


class ModifyProblem(FlaskForm):

    '''
        define form about Modify Problem
    '''

    school_id = SelectField(u'School', coerce=int)
    title = StringField(u'Title', validators=[DataRequired()])
    time_limit = IntegerField(u'Time Limit', validators=[DataRequired()])
    memory_limit = IntegerField(u'Memory Limit', validators=[DataRequired()])
    special_judge = BooleanField(u'Special Judge')
    type = SelectField(u'Type', coerce=int)
    submission_num = IntegerField(u'Submissions')
    accept_num = IntegerField(u'Accepted')
    description = TextAreaField(u'Description')
    input = TextAreaField(u'Input')
    output = TextAreaField(u'Output')
    sample_input = TextAreaField(u'Sample Input')
    sample_output = TextAreaField(u'Sample Output')
    source_name = StringField(u'Source', validators=[Length(0, 64)])
    hint = TextAreaField(u'Hint')
    author = StringField(u'Author', validators=[Length(0, 64)])
    visible = BooleanField(u'Visibility')
    tags = SelectMultipleField(u'Tag', coerce=int)
    submit = SubmitField(u'Submit')


    def __init__(self, *args, **kwargs):

        '''
            init settings about ModifyProblem
        :param args: args
        :param kwargs: kwargs
        '''

        super(ModifyProblem, self).__init__(*args, **kwargs)
        self.school_id.choices = [(school.id, school.school_name)
                              for school in SchoolList.query.order_by(SchoolList.school_name).all()]
        self.tags.choices = [(tag.id, tag.tag_name)
                             for tag in Tag.query.order_by(Tag.tag_name).all()]
        self.type.choices = [(1, u'ACM'), (2, u'NOIP')]


class ModifyTag(FlaskForm):

    '''
        define form about TagModify
    '''

    tag_name = StringField(u'Tag Name', validators=[DataRequired(), Length(0, 32)])
    submit = SubmitField(u'Submit')

    def validate_tag_name(self, field):

        '''
            judge the email field is good for our need
        :param field: field
        :return: None
        '''

        if Tag.query.filter_by(tag_name=field.data).first():
            raise ValidationError(u'Tag Name has already appeared!')


class ModifyUser(FlaskForm):

    '''
        define form about ModifyUser
    '''

    email = StringField(u'Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, u'Username can only contain 0-9,a-z,A-z')])
    nickname = StringField(u'Nickname', validators=[Length(0, 64)])
    confirmed = BooleanField(u'Confirm')
    role_id = SelectField(u'Role', coerce=int)
    challenge_level = IntegerField(u'Challenge Level')
    password = StringField(u'Password')
    gender = SelectField(u'Gender', coerce=unicode)
    major = StringField(u'Major', validators=[Length(0, 64)])
    degree = SelectField(u'Degree', coerce=unicode)
    country = SelectField(u'Country', coerce=unicode)
    address = StringField(u'Address', validators=[Length(0, 128)])
    school_id = SelectField(u'School', coerce=int)
    phone_num = StringField(u'Phone', validators=[Length(0, 32)])
    student_num = StringField(u'Number', validators=[Length(0, 64)])
    about_me = TextAreaField(u'Description', validators=[Length(0, 1024)])
    submit = SubmitField(u'Submit')

    def __init__(self, user, *args, **kwargs):

        '''
            init settings about ModifyUser class
        :param user: a user
        :param args: args
        :param kwargs: kwargs
        '''

        super(ModifyUser, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user
        self.gender.choices = [(current_app.config['GENDER'][k][0], current_app.config['GENDER'][k][1])
                               for k in range(0, len(current_app.config['GENDER']))]
        self.degree.choices = [(current_app.config['DEGREE'][k][0], current_app.config['DEGREE'][k][1])
                               for k in range(0, len(current_app.config['DEGREE']))]
        self.country.choices = [(current_app.config['COUNTRY'][k][0], current_app.config['COUNTRY'][k][1])
                                for k in range(0, len(current_app.config['COUNTRY']))]
        self.school_id.choices = [(school.id, school.school_name)
                                  for school in SchoolList.query.order_by(SchoolList.school_name).all()]

    def validate_email(self, field):

        '''
            judge the email field is good for our need
        :param field: field
        :return: None
        '''

        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'Email has been registed!')

    def validate_username(self, field):

        '''
            judge the username field is good for our need
        :param field: field
        :return: None
        '''

        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'Username has been registed!.')


class ModifySchoolStatus(FlaskForm):

    '''
        define Modify OJ status form
    '''

    school_name = StringField(u'School Name', validators=[InputRequired(), Length(0, 128)])
    description = TextAreaField(u'Description')
    # url = StringField(u'学校地址', validators=[InputRequired(), Length(0, 128)])
    # vjudge = BooleanField(u'vjudge')
    # status = SelectField(u'学校状态', validators=[InputRequired()], choices=[('0', u'负载较重'), ('1', u'一般'), ('2', u'正常')])
    submit = SubmitField(u'Submit')


class ModifySubmissionStatus(FlaskForm):

    '''
        define Modify submission status form
    '''

    status = SelectField(u'Judge Status', validators=[InputRequired()], coerce=int)
    exec_time = IntegerField(u'Time Used', validators=[InputRequired()])
    exec_memory = IntegerField(u'Memory Used', validators=[InputRequired()])
    visible = BooleanField(u'Visibility')
    submit = SubmitField(u'Submit')

    def __init__(self, *args, **kwargs):
        super(ModifySubmissionStatus, self).__init__(*args, **kwargs)
        self.status.choices = [(int(current_app.config['LOCAL_SUBMISSION_STATUS'][k]), k)
                               for k in current_app.config['LOCAL_SUBMISSION_STATUS']]


class ModifySubmissionStatus4Noip(FlaskForm):

    '''
        define Modify submission status form
    '''

    status = FloatField(u'Judge Status', validators=[InputRequired()])
    exec_sub = StringField(u'Score Points', validators=[])
    visible = BooleanField(u'Visibility')
    submit = SubmitField(u'Submit')


class ModifyBlog(FlaskForm):

    '''
        define Modify Blog form
    '''

    title = StringField(u'Title', validators=[InputRequired(), Length(0, 64)])
    content = TextAreaField(u'Content', validators=[InputRequired()])
    public = BooleanField(u'Visibility')
    submit = SubmitField(u'Submit')


class ModifyContest(FlaskForm):

    '''
        define Modify Contest Form
    '''

    contest_name = StringField(u'Title', validators=[DataRequired(), Length(0, 128)])
    start_time = DateTimeField(u'Start', format='%Y-%m-%d %H:%M')
    end_time = DateTimeField(u'End', format='%Y-%m-%d %H:%M')
    school_id = SelectField(u'School', coerce=int)
    type = SelectField(u'Type', coerce=int, validators=[DataRequired()])
    rule = SelectField(u'Role', coerce=int, validators=[DataRequired()])
    password = StringField(u'Contest Password', validators=[Length(0, 64)])
    description = TextAreaField(u'Description')
    announce = TextAreaField(u'Announcement', validators=[Length(0, 1024)])
    visible = BooleanField(u'Visibility')
    manager = StringField(u'Administrator Username', validators=[DataRequired()])
    rank_frozen = BooleanField(u'Freeze Ranklist')
    submit = SubmitField(u'Submit')

    def __init__(self, *args, **kwargs):

        '''
            init settings about ModifyContest class
        :param args: args
        :param kwargs: kwargs
        '''

        super(ModifyContest, self).__init__(*args, **kwargs)
        self.type.choices = [(1, u'Open'), (2, u'Private(Admin confirm)'), (3, u'Private(password protected)'), (4, u'Onsite preregist'), (5, u'Onsite/Official')]
        self.rule.choices = [(1, u'ACM rule'), (2, u'OI rule') ]
        #before OI contest FINISH:
        #self.rule.choices = [(1, u'ACM规则(OI规则尚未开放)')]
        self.school_id.choices = [(school.id, school.school_name)
                                  for school in SchoolList.query.order_by(SchoolList.school_name).all()]

    def validate_manager(self, field):

        '''
            check if the manager is good
        :param field: form field
        :return: True or False
        '''

        if User.query.filter_by(username=field.data).first() is None:
            raise ValidationError(u'Admin not existed!')


class AddContestProblem(FlaskForm):

    '''
        define Add contest problem form
    '''

    problem_id = IntegerField(u'Problem ID', validators=[DataRequired()])
    problem_alias = StringField(u'Problem Title', validators=[Length(0, 64)])
    submit = SubmitField(u'Submit')


class ContestUserInsert(FlaskForm):

    '''
        define add contest user form
    '''

    user_list = TextAreaField(u'User .csv info', validators=[DataRequired()])
    submit = SubmitField(u'Submit')


class ModifyAnnounce(FlaskForm):

    '''
        define modify announce form
    '''

    blog_id = IntegerField(u'Blog ID', validators=[InputRequired()])
    submit = SubmitField(u'Submit')


class ModifyChallenge(FlaskForm):

    '''
        define modify challenge form
    '''

    challenge_name = StringField(u'Challenge Name', validators=[DataRequired(), Length(0, 64)])
    challenge_level = IntegerField(u'Challenge Level', validators=[DataRequired()])
    submit = SubmitField(u'Submit')


class ModifyChallengeRound(FlaskForm):

    '''
        define modify challenge round form
    '''

    round_name = StringField(u'Round Name', validators=[DataRequired(), Length(0, 64)])
    challenge_id = SelectField(u'Challenge belongs', coerce=int)
    submit = SubmitField(u'Submit')

    def __init__(self, *args, **kwargs):

        '''
            init settings about ModifyContest class
        :param args: args
        :param kwargs: kwargs
        '''

        super(ModifyChallengeRound, self).__init__(*args, **kwargs)
        self.challenge_id.choices = [(challenge.id, challenge.challenge_name)
                                  for challenge in Challenge.query.order_by(Challenge.challenge_level.asc()).all()]