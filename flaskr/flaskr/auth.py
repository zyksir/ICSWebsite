# -*- coding: utf-8 -*-
# author: zyk
# A Blueprint is a way to organize a group of related views and other code.
# Rather than registering views and other code directly with an application,
# they are registered with a blueprint.


import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import *

bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_register_info(form):
    username = request.form['username']
    password = request.form['password']
    nickname = request.form['nickname']
    repassword = request.form['repassword']
    email = request.form['email']
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif not repassword:
        error = 'Repassword is required'
    elif not (password == repassword):
        error = 'Two passwords are inconsistent.'
    elif ((len(password) < 6) or (len(password) > 16)):
        error = 'The length of password should be between 6 and 16.'
    elif len(username) > 40:
        error = 'The maximum size of username is 40, your username is too long!'
    elif len(nickname) > 40:
        error = 'The maximum size of nickname is 40, your username is too long!'
    elif not (password == repassword):
        error = 'you enter different passwords!'
    elif len(user.select(user.id).where(user.username == username))>0 :
    # elif db.execute(
    #         'SELECT id FROM user WHERE username = %s', (username,)
    # ) > 0:
        error = 'User {} is already registered.'.format(username)

    return username, password, nickname, email, error
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        print(request.form)
        username, password, nickname, email, error = get_register_info(request.form)
        # conn, db = get_db()

        if error is None:
            user.insert({
                user.username: username,
                user.password: password,
                user.nickname: nickname,
                user.email: email
            }).execute()
            # db.execute(
            #     'INSERT INTO user (username, nickname, password, email, is_block) VALUES (%s, %s, %s, %s, %s)',
            #     (username, nickname, generate_password_hash(password), email, is_block)
            # )
            # conn.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/temp_reg.html')

def get_login_info(form):
    username = form['username']
    password = form['password']
    error = None
    User = user.select().where(user.username == username)
    if len(User) == 0:
        error = "用户名不存在"
    else:
        User = User.get()
        if not check_password_hash(User.password, password):
            error = "密码不正确"

    if error == None:

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        # conn, db = get_db()
        # error = None
        # num = db.execute(
        #     'SELECT * FROM user WHERE username = %s', (username,)
        # )
        # user = db.fetchone()

        # if num == 0:
        #     error = '用户名不存在！'
        # elif not check_password_hash(user['password'], password):
        #     error = '密码不正确！'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # if user['id'] == 1:
            #     return redirect(url_for('admin.admin_home'))
            return redirect(url_for('index'))

        flash(error)    # stores messages that can be retrieved when rendering the template.

    return render_template('auth/temp_login.html')


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
            redirect(url_for('blog.index'))

        return view(**kwargs)

    return wrapped_view