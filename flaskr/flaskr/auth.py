# -*- coding: utf-8 -*-
# author: zyk
# A Blueprint is a way to organize a group of related views and other code. Rather than registering views and other code directly with an application, they are registered with a blueprint.


import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn, db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif len(username) > 40:
            error = 'The maximum size of username is 40, your username is too long!'
        elif not password:
            error = 'Password is required.'
        elif len(password) > 40:
            error = 'The maximum size of password is 40, your password is too long!'
        elif db.execute(
            'SELECT id FROM user WHERE username = %s', (username,)
        ) > 0:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (%s, %s)',
                (username, generate_password_hash(password))
            )
            conn.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn, db = get_db()
        error = None
        num = db.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        user = db.fetchone()

        if num == 0:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)    # stores messages that can be retrieved when rendering the template.

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn, db = get_db()
        db.execute(
            'SELECT * FROM user WHERE id = %s', (user_id,)
        )
        g.user = db.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view