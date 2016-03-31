#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Jan Rygl <jimmy@rare-technologies.com>
# Copyright (C) 2015 RaRe Technologies s.r.o. <info@rare-technologies.com>
# All Rights Reserved

import time
import os
from collections import defaultdict
import logging
import itertools

from flask import Flask, request, session, g, redirect, url_for, abort, flash
from flask.ext.mako import MakoTemplates, render_template

from evaluate import AnnotationInterface
from config import data_path, sqldict_path

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.template_folder = "templates"
app.secret_key = '[l=xPsQ\x88\xc4\x19\r\xdf\x06\xb2\xa6\xfa$\x114\x97?\xc3\xab\x9f\xe2'
app.debug = True
mako = MakoTemplates(app)


ai = AnnotationInterface(data_path, sqldict_path)


def get_user_stats(username):
    """For given user, find number of annotated and skipped listings.

    :param username: searched user
    :return: two dictionaries {'done': count, 'skipped': count}
    """

    return ai.get_stats(username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'Username: your surname'
        elif request.form['password'] != "rare":
            error = 'Invalid password'
        else:
            # check for similar nicks
            username = str(request.form['username']).strip()
            session['logged_in'] = True
            session['username'] = username
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.mako', error=None, login_error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/help', methods=['GET', 'POST'])
def annotations_manual():
    return render_template('annotation_manual.mako', error=None)


@app.route('/admin')
def admin():

    return render_template(
        'admin.mako',
        agreement=ai.agreement(),
        score=ai.score(),
        export=ai.export(),
        error=None,
        stats=get_user_stats(session["username"])
        )


@app.route('/', methods=['GET', 'POST'])
def index():
    # not logged in, redirect
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    # process POST request
    if request.method == 'POST':
        ai.save(request.form, session['username'])

    record = ai.get(session['username'])

    return render_template(
        'presenter.mako',
        error=None,
        input=record,
        session=session,
        stats=get_user_stats(session["username"]))


if __name__ == '__main__':
    mako.run()
