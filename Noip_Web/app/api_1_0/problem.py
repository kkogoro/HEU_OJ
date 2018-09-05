#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from flask import jsonify, request, g, abort, url_for, current_app
from ..exceptions import ValidationError
from .. import db
from ..models import Problem, SchoolList, Permission
from . import api
from .decorators import permission_required

@api.route('/problem/<int:id>')
@permission_required(Permission.JUDGER)
def get_problem(id):

    '''
        deal with operation of getting problem detail with id
    :param id:  problem id
    :return: problem in json
    '''

    problem = Problem.query.get_or_404(id)
    return jsonify(problem.to_json())
