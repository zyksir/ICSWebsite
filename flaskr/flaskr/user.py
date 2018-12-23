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
from peewee import *

from playhouse.shortcuts import model_to_dict

bp = Blueprint('user', __name__, url_prefix='/user')

from .db import *


@bp.route('/home/<string:id>')
def home(id):
    '''conn, db = get_db()
    db.execute('SELECT username, nickname, email, created FROM user WHERE id=%s', (id,))
    tmp_list = db.fetchone() '''

    from .db import user
    tmp_list = model_to_dict(user.select(user.username, user.nickname, user.email, user.created).where(user.id == id).get())

    '''db.execute(
        'SELECT p.id, p.title, p.created, p.author_id'
        ' FROM post p'
        ' WHERE p.author_id = %s'
        ' ORDER BY created DESC',
        (id,)
    )
    posts = db.fetchall()
    #pprint(posts) '''

    posts = []
    allposts = post.select(post.id, post.title, post.created, post.author_id).where(post.author_id == id).order_by(post.created.desc())
    for apost in allposts:
        posts.append(model_to_dict(apost))

    '''db.execute(
        'SELECT c.author_id, c.post_id'
        ' FROM collects c'
        ' WHERE c.author_id = %s ',
        (id)
    )
    collects = db.fetchall() '''

    return_collects = []
    allcollects = collects.select(collects.author_id, collects.post_id).where(collects.author_id == id)
    for acollect in allcollects:
        dctcollect = model_to_dict(acollect)
        apost = model_to_dict(post.select(post.title, post.created).where(post.id == dctcollect['post_id']).get())
        dctcollect['title'] = apost['title']
        dctcollect['created'] = apost['created']
        dctcollect['id'] = dctcollect['post_id']

        return_collects.append(dctcollect)

    '''for acollect in collects:
        pprint(acollect)
        db.execute(
            'SELECT p.title, p.created'
            ' FROM post p'
            ' WHERE p.id = %s',
            (acollect['post_id'])
        )
        apost = db.fetchone()
        acollect['title'] = apost['title']
        acollect['created'] = apost['created']
        acollect['id'] = acollect['post_id']'''
    return_collects = return_collects[::-1]
    pprint(return_collects)

    user = {
        'username': tmp_list['username'],
        'nickname': tmp_list['nickname'],
        'email': tmp_list['email'],
        'created': tmp_list['created'],
        'posts': posts,
        'markposts': return_collects
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
            '''conn, db = get_db()
            db.execute(
                'UPDATE user SET nickname = %s'
                ' WHERE id = %s',
                (nickname, g.user['id'])
            )
            conn.commit() '''

            t = user.update(nickname=nickname).where(user.id == g.user['id'])
            t.execute()

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
            '''conn, db = get_db()
            db.execute(
                'UPDATE user SET email = %s'
                ' WHERE id = %s',
                (email, g.user['id'])
            )
            conn.commit() '''

            t = user.update(email=email).where(user.id == g.user['id'])
            t.execute()

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

        '''conn, db = get_db()
        db.execute(
            'SELECT password FROM user WHERE id = %s', (g.user['id'],)
        )
        real_password = db.fetchone()['password'] '''

        real_password = model_to_dict(user.select(user.password).where(user.id == g.user['id']).get())['password']

        #print(real_password)
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
            '''conn, db = get_db()
            db.execute(
                'UPDATE user SET password = %s'
                'WHERE id = %s',
                (generate_password_hash(password), g.user['id'])
            )
            conn.commit() '''

            t = user.update(password=generate_password_hash(password)).where(user.id == g.user['id'])
            t.execute()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setpass.html')
