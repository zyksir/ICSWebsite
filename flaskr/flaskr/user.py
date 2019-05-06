from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import subprocess

from .auth import login_required
from pprint import pprint
from .db import *
from playhouse.shortcuts import model_to_dict

bp = Blueprint('user', __name__, url_prefix='/user')


def get_home_info(id):
    conn, db = get_db()
    db.execute(
        'SELECT * FROM user WHERE user.id = %s', (id)
    )
    tmp_list = db.fetchone()
    # print(tmp_list)
    # tmp_list = model_to_dict(user.select(user.username, user.nickname, user.email, user.created).where(user.id == id).get())
    # print(tmp_list)

    db.execute(
        'SELECT id, title, created, author_id FROM post as p WHERE p.author_id = %s ORDER BY p.created DESC', (id)
    )
    posts = db.fetchall()
    # print(posts)
    # posts = []
    # allposts = post.select(post.id, post.title, post.created, post.author_id).where(post.author_id == id).order_by(post.created.desc())
    # for apost in allposts:
    #     posts.append(model_to_dict(apost)

    db.execute(
        'SELECT c.author_id, c.post_id, p.title, p.created, p.id '
        'FROM collects as c INNER JOIN post as p '
        'ON c.post_id = p.id '
        'WHERE c.author_id = %s'
        , (id)
    )
    return_collects = db.fetchall()
    # print(return_collects)
    # return_collects = []
    # allcollects = collects.select(collects.author_id, collects.post_id).where(collects.author_id == id)
    # for acollect in allcollects:
    #     dctcollect = model_to_dict(acollect)
    #     apost = model_to_dict(post.select(post.title, post.created).where(post.id == dctcollect['post_id']).get())
    #     dctcollect['title'] = apost['title']
    #     dctcollect['created'] = apost['created']
    #     dctcollect['id'] = dctcollect['post_id']
    #
    #     return_collects.append(dctcollect)
    #
    # return_collects = return_collects[::-1]
    # pprint(return_collects)

    user_info = {
        'username': tmp_list['username'],
        'nickname': tmp_list['nickname'],
        'email': tmp_list['email'],
        'created': tmp_list['created'],
        'posts': posts,
        'markposts': return_collects
        }

    return user_info


@bp.route('/home/<string:id>')
def home(id):
    user_info = get_home_info(id)

    return render_template('user/temp_home.html', user=user_info)


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
                'UPDATE user SET nickname = %s WHERE user.id = %s', (nickname, g.user['id'])
            )
            conn.commit()
            # t = user.update(nickname=nickname).where(user.id == g.user['id'])
            # t.execute()

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
                'UPDATE user SET email = %s WHERE user.id = %s', (email, g.user['id'])
            )
            conn.commit()
            # t = user.update(email=email).where(user.id == g.user['id'])
            # t.execute()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setemail.html')


@bp.route('/setpass', methods=('GET', 'POST'))
def setpass():
    if request.method == 'POST':
        nowpass = request.form['nowpass']
        password = request.form['password']
        repassword = request.form['repassword']
        error = None

        conn, db = get_db()
        db.execute(
            "SELECT password FROM user WHERE id = %s", (g.user['id'])
        )
        real_password = db.fetchone()["password"]
        # print(real_password)
        # real_password = model_to_dict(user.select(user.password).where(user.id == g.user['id']).get())['password']

        if not (check_password_hash(real_password, nowpass)):
            error = 'Wrong password!'

        if not password:
            error = 'Password is required.'
        elif not (password ==repassword):
            error = 'Two passwords are inconsistent.'
        elif not (password == repassword):
            error = 'you enter different passwords!'
        elif ((len(password) < 6) or (len(password) > 16)):
            error = 'The length of password should be between 6 and 16.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE user SET password = %s WHERE user.id = %s', (generate_password_hash(password), g.user['id'])
            )
            conn.commit()
            # t = user.update(password=generate_password_hash(password)).where(user.id == g.user['id'])
            # t.execute()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setpass.html')
