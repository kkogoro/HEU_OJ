#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField, IntegerField, ValidationError
from wtforms.validators import DataRequired
from flask import current_app


class SubmitForm(FlaskForm):

    '''
        define form of submitting code
    '''

    problem_id = IntegerField(u'Problem ID', validators=[DataRequired()])
    language = SelectField(u'Language', coerce=int)
    code = TextAreaField(u'Code', validators=[DataRequired()])
    submit = SubmitField(u'Submit')


    def validate_code(self, field):

        '''
            validate data of code field
        :param field: field
        :return: Null
        '''

        if len(field.data) < 10 or len(field.data) > 65535:
            raise ValidationError(u'Code length should in [10,65535]')

    def __init__(self, *args, **kwargs):

        '''
            init function
        :param args: args
        :param kwargs: kwargs
        '''

        super(SubmitForm, self).__init__(*args, **kwargs)
        self.language.choices = [(current_app.config['LOCAL_LANGUAGE'][k], k)
                                 for k in current_app.config['LOCAL_LANGUAGE'].keys()]
