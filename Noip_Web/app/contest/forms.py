#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, PasswordField, DateField, \
    IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional, NumberRange
from wtforms import ValidationError
from ..models import Role, User, Permission, SchoolList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag
from flask import current_app


class PasswordRegisterForm(Form):

    '''
        define form of password register
    '''

    contest_password = StringField(u'Contest Password', validators=[DataRequired(), Length(0, 64)])
    submit = SubmitField(u'Submit')


class SubmitForm(Form):

    '''
        define form of submit code
    '''
    language = SelectField(u'Language', coerce=int)
    code = TextAreaField(u'Code', validators=[DataRequired()])
    submit = SubmitField(u'Submit')

    def validate_code(self, field):
        if len(field.data) < 10 or len(field.data) > 65535:
            raise ValidationError(u'Code length should in [10,65535]')

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.language.choices = [(current_app.config['LOCAL_LANGUAGE'][k], k)
                                 for k in current_app.config['LOCAL_LANGUAGE'].keys()]