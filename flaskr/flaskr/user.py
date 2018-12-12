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


@bp.route('/set', methods=('GET', 'POST'))
def set():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email']
        error = None

        if not nickname:
            error = 'Nickname is required.'
        if not email:
            error = 'Email is required.'

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()
            db.execute(
                'UPDATE user SET nickname = %s, email = %s'
                ' WHERE id = %s',
                (nickname, email, g.user['id'])
            )
            conn.commit()

            return redirect(url_for('blog.index'))

    return render_template('user/easy_set.html')