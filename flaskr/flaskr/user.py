from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import subprocess

from flaskr.auth import login_required
from flaskr.db import get_db

from pprint import pprint

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/home/<string:id>')
def home(id):
    conn, db = get_db()
    db.execute('SELECT username, nickname, email, created FROM user WHERE id=%s', (id,))
    tmp_list = db.fetchall()
    #print(tmp_list)
    user = {
        'username': tmp_list[0]['username'],
        'nickname': tmp_list[0]['nickname'],
        'email': tmp_list[0]['email'],
        'created': tmp_list[0]['created'],
        'posts': [],
        'markposts': []
        }
    return render_template('user/temp_home.html', user=user)


@bp.route('/setname', methods=('GET', 'POST'))
def setname():
    if request.method == 'POST':
        nickname = request.form['nickname']
        error = None

        if not nickname:
            error = 'Nickname is required.'

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()
            db.execute(
                'UPDATE user SET nickname = %s'
                ' WHERE id = %s',
                (nickname, g.user['id'])
            )
            conn.commit()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setnickname.html')


@bp.route('/setemail', methods=('GET', 'POST'))
def setemail():
    if request.method == 'POST':
        email = request.form['email']
        error = None

        if not email:
            error = 'Email is required.'

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()
            db.execute(
                'UPDATE user SET email = %s'
                ' WHERE id = %s',
                (email, g.user['id'])
            )
            conn.commit()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setemail.html')


@bp.route('/setpass', methods=('GET', 'POST'))
def setpass():
    if request.method == 'POST':
        '''
        nowpass 原来的密码
        password 新的密码
        repassword 重新输入新密码
        if not后的东西要重写
        以及error可以中文，应该是可以输出到前端的如果我没写错的话
        '''
        nowpass = request.form['nowpass']
        password = request.form['password']
        repassword = request.form['repassword']
        error = None

        if not password:
            error = 'Password is required.'
        elif not (password ==repassword):
            error = 'Two passwords are inconsistent.'
        elif not (password == repassword):
            error = 'you enter different passwords!'

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()
            db.execute(
                'UPDATE user SET password = %s'
                ' WHERE id = %s',
                (password, g.user['id'])
            )
            conn.commit()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setpass.html')