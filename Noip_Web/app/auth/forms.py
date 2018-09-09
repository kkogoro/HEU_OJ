#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired, InputRequired
from wtforms import ValidationError
from ..models import User, SchoolList
from flask import current_app

class LoginForm(FlaskForm):

    '''
        define login form
    '''

    username = StringField(u'Username', validators=[DataRequired(), Length(1, 64),
                                               Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, u'username may only contain letters and numbers and should be starts with letter.')])
    password = PasswordField(u'Password', validators=[DataRequired()])
    remember_me = BooleanField(u'Remember me', default=False)
    submit = SubmitField(u'Login')


class RegistrationForm(FlaskForm):

    '''
        define register form
    '''

    email = StringField(u'Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, u'username may only contain letters and numbers and should be starts with letter.')])
    school_id = SelectField(u'School', validators=[InputRequired()], coerce=int)
    password = PasswordField(u'Password', validators=[DataRequired(), EqualTo('password2', message=u'Password not the same.')])
    password2 = PasswordField(u'Confirm Password', validators=[DataRequired()])
    submit = SubmitField(u'Register')

    def __init__(self, *args, **kwargs):

        '''
            init settings about ModifyUser class
        :param user: a user
        :param args: args
        :param kwargs: kwargs
        '''

        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.school_id.choices = [(school.id, school.school_name)
                                  for school in SchoolList.query.order_by(SchoolList.school_name).all()]

    def validate_email(self, field):

        '''
            judge if the email has already registed
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'Email has been registered!')

    def validate_username(self, field):

        '''
            judge if the username has already registed
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'Username has been registered!')

    def validate_password(self, field):

        '''
            judge if the password length is bigger than 6
        :param field: field
        :return: Null
        '''

        if len(field.data) < 6:
            raise ValidationError(u'Password should be longer than 6 characters.')


class ChangePasswordForm(FlaskForm):

    '''
        define change password form
    '''

    old_password = PasswordField(u'Old Password', validators=[DataRequired()])
    password = PasswordField(u'New Password', validators=[DataRequired(), EqualTo('password2', message=u'Password not the same')])
    password2 = PasswordField(u'Confirm New Password', validators=[DataRequired()])
    submit = SubmitField(u'Update')

    def validate_password(self, field):

        '''
            judge if the password length is bigger than 6
        :param field: field
        :return: Null
        '''

        if len(field.data) < 6:
            raise ValidationError(u'Password should be longer than 6 characters.')


class PasswordResetRequestForm(FlaskForm):

    '''
        define request password reset form
    '''

    email = StringField(u'Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField(u'Send')


class PasswordResetForm(FlaskForm):

    '''
        define password reset form
    '''

    email = StringField(u'Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'New Password', validators=[DataRequired(), EqualTo('password2', message=u'Password not the same')])
    password2 = PasswordField(u'Confirmed New Password', validators=[DataRequired()])
    submit = SubmitField(u'Reset')

    def validate_email(self, field):

        '''
            judge if the email is good to use
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'Invalid Email')

    def validate_password(self, field):

        '''
            judge if the password length is bigger than 6
        :param field: field
        :return: Null
        '''

        if len(field.data) < 6:
            raise ValidationError(u'Password should be longer than 6 characters.')


class ChangeEmailForm(FlaskForm):

    '''
        define change email form
    '''

    email = StringField(u'New Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'Password', validators=[DataRequired()])
    submit = SubmitField(u"Update")

    def validate_email(self, field):

        '''
            judge if the email is good to use
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'Email has been registered')


class EditProfileForm(FlaskForm):

    '''
        define edit profile form
    '''

    nickname = StringField(u'Nickname', validators=[DataRequired(), Length(0, 64)])
    realname = StringField(u'Realname', validators=[Length(0, 64)])
    gender = SelectField(u'Gender', coerce=unicode)
    major = StringField(u'Major', validators=[Length(0, 64)])
    degree = SelectField(u'Degree', coerce=unicode)
    country = SelectField(u'Country', coerce=unicode)
    address = StringField(u'Address', validators=[Length(0, 128)])
    #school_id = SelectField(u'学校', validators=[InputRequired()], coerce=int)
    student_num = StringField(u'Number', validators=[Length(0, 64)])
    phone_num = StringField(u'Phone', validators=[Length(0, 32), Regexp('0?(13|14|15|17|18)[0-9]{9}', 0, u'Invalid phonenumber.')])
    about_me = TextAreaField(u'Description', validators=[Length(0, 1024)])
    submit = SubmitField(u'Submit')

    def __init__(self, *args, **kwargs):

        '''
            init func to deal with the choices
        :param args: args
        :param kwargs: kwargs
        '''

        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.gender.choices = [(current_app.config['GENDER'][k][0], current_app.config['GENDER'][k][1])
                               for k in range(0, len(current_app.config['GENDER']))]
        self.degree.choices = [(current_app.config['DEGREE'][k][0], current_app.config['DEGREE'][k][1])
                               for k in range(0, len(current_app.config['DEGREE']))]
        self.country.choices = [(current_app.config['COUNTRY'][k][0], current_app.config['COUNTRY'][k][1])
                               for k in range(0, len(current_app.config['COUNTRY']))]
        '''
        self.school_id.choices = [(school.id, school.school_name)
                                  for school in SchoolList.query.order_by(SchoolList.school_name).all()]
        '''