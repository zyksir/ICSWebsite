from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import subprocess
import json

from flaskr.auth import login_required
from flaskr.db import *
from flaskr.blog import get_post, delete_post, delete_reply
from playhouse.shortcuts import model_to_dict
from pprint import pprint

bp = Blueprint('admin', __name__)

def modify_is_top(post_id, is_top):
    post.update({post.is_top: is_top}).where(post.id == post_id).execute()
    # conn, db = get_db()
    # db.execute(
    #     'UPDATE post SET is_top = %s'
    #     ' WHERE id = %s',
    #     (is_top, post_id)
    # )
    # conn.commit()
def modify_is_file(post_id, is_fine):
    post.update({post.is_top: is_fine}).where(post.id == post_id).execute()
    # conn, db = get_db()
    # db.execute(
    #     'UPDATE post SET is_fine = %s'
    #     ' WHERE id = %s',
    #     (is_fine, post_id)
    # )
    # conn.commit()
def modify_is_block(user_id, is_block):
    user.update({user.is_block: is_block}).where(user.id == user_id).execute()
    # conn, db = get_db()
    # db.execute(
    #     'UPDATE user SET is_block = %s'
    #     ' WHERE id = %s',
    #     (is_block, user_id)
    # )
    # conn.commit()

def SearchPost(ST):
    s = "%" + ST + "%"
    # conn, db = get_db()
    # db.execute(
    #     'SELECT p.id, title, body, p.created, author_id, username, nickname , p.is_top, p.is_fine'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' WHERE title LIKE %s'
    #     ' ORDER BY created DESC',
    #     (s)
    # )
    # users = db.fetchall()
    Posts = post.select().where((post.title ** s) | (post.body ** s))
    posts = []
    for Post in Posts:
        tmp_dict = model_to_dict(Post)
        tmp_dict['nickname'] = tmp_dict['author']['nickname']
        posts.append(tmp_dict)
    pprint(posts)
    return posts

def SearchMember(ST):
    s = "%" + ST + "%"
    # conn, db = get_db()
    # db.execute(
    #     'SELECT p.id, title, body, p.created, author_id, username, nickname , p.is_top, p.is_fine'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' WHERE title LIKE %s'
    #     ' ORDER BY p.id DESC',
    #     (s)
    # )
    # users = db.fetchall()
    Users = user.select().where((user.nickname ** s) | (user.username ** s))
    users = []
    for User in Users:
        users.append(model_to_dict(User))
    pprint(users)
    return users

def SearchDoc(ST):
    s = "%" + ST + "%"
    Files = post_file.select().where((post_file.filename ** s))
    files = []
    for File in Files:
        tmp_dict = model_to_dict(File)
        tmp_dict['nickname'] = tmp_dict['post']['author']['nickname']
        tmp_dict['username'] = tmp_dict['post']['author']['username']
        files.append(tmp_dict)
    pprint(files)
    # conn, db = get_db()
    # db.execute(
    #     'SELECT id, created, filename, post_id'
    #     ' FROM post_file'
    #     'WHERE filename LIKE %s'
    #     ' ORDER BY created DESC',
    #     (s)
    # )
    # posts = db.fetchall()
    # for i, post in enumerate(posts):
    #     db.execute(
    #         'SELECT author_id'
    #         ' FROM post WHERE id=%s',
    #         (post['post_id'],)
    #     )
    #     post_info = db.fetchall()
    #     posts[i]['author_id'] = post_info[0]['author_id']
    #     db.execute(
    #         'SELECT username, nickname'
    #         ' FROM user WHERE id=%s',
    #         (posts[i]['author_id'],)
    #     )
    #     user_info = db.fetchall()
    #     posts[i]['username'] = user_info[0]['username']
    #     posts[i]['nickname'] = user_info[0]['nickname']
    return files


@bp.route('/admin', methods=('GET', 'POST'))
@login_required
def admin_home():
    conn, db = get_db()
    db.execute('SELECT id, created, username, nickname FROM user')
    post = db.fetchall()[0]
    return render_template('new_index.html', post=post)

def ViewDeleteMember():
    return render_template('new_index.html')
def ViewDeletePost():
    return render_template('new_index.html')



@bp.route('/member', methods=('GET', 'POST'))
@login_required
def Member():
    if request.method == 'POST':
        ST = request.form['title']
        posts = SearchMember(ST)
        return render_template('new_member.html', posts=posts)

    conn, db = get_db()
    db.execute(
        'SELECT id, created, username, nickname , email, is_block'
        ' FROM user WHERE id > 1'
        ' ORDER BY created DESC'
    )
    posts = db.fetchall()
    # length = len(posts)
    # pprint(posts)
    return render_template('new_member.html', posts=posts)
@bp.route('/delete_member/<int:id>', methods=('POST', ))
@login_required
def DeleteMember(id):
    print("Delete No %d"%id)
    conn, db = get_db()
    # first we select all the posts related to user id and delete them
    db.execute('SELECT id FROM post WHERE author_id=%s', (id,))
    post_list = db.fetchall()
    print(post_list)
    for post in post_list:
        delete_post(post['id'])

    # second we delect all the replies
    db.execute('SELECT id FROM reply WHERE author_id=%s', (id,))
    reply_list = db.fetchall()
    print(reply_list)
    for reply in reply_list:
        delete_reply(reply['id'])

    # finally we delect all the personal info
    db.execute('DELETE FROM user WHERE id = %s', (id,))
    conn.commit()

    return redirect(url_for('admin.Member'))
@bp.route('/block_member/<string:id>', methods=('POST', ))
@login_required
def BlockMember(id):
    id = eval(id)
    print(id)
    modify_is_block(id[0], id[1])
    return redirect(url_for('admin.Member'))

@bp.route('/post', methods=('GET', 'POST'))
@login_required
def Post():
    if request.method == 'POST':
        ST = request.form['title']
        posts = SearchPost(ST)
        return render_template('new_post.html', posts=posts)
    conn, db = get_db()
    db.execute(
        'SELECT p.id, title, body, p.created, author_id, username, nickname , p.is_top, p.is_fine'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = db.fetchall()
    length = len(posts)
    posts = sorted(posts, key=lambda p: p['created'], reverse=True)
    for i, post in enumerate(posts):
        db.execute(
            'SELECT id, post_id, filename, filehash'
            ' FROM post_file WHERE post_id=%s'
            ' ORDER BY created DESC',
            (post['id'],)
        )
        post['files'] = db.fetchall()
    return render_template('new_post.html', posts=posts)
@bp.route('/delete_post/<int:id>', methods=('GET', 'POST'))
@login_required
def DeletePost(id):
    delete_post(id)
    return redirect(url_for('admin.Post'))
@bp.route('/top_post/<string:id>', methods=('GET', 'POST'))
@login_required
def TopPost(id):
    id = eval(id)
    print(id)
    modify_is_top(id[0], id[1])
    return redirect(url_for('admin.Post'))

@bp.route('/doc', methods=('GET', 'POST'))
@login_required
def Doc():
    if request.method == 'POST':
        ST = request.form['title']
        posts = SearchDoc(ST)
        return render_template('new_doc.html', posts=posts)
    conn, db = get_db()
    db.execute(
        'SELECT id, created, filename, post_id'
        ' FROM post_file'
        ' ORDER BY created DESC'
    )
    posts = db.fetchall()
    for i, post in enumerate(posts):
        db.execute(
            'SELECT author_id'
            ' FROM post WHERE id=%s',
            (post['post_id'],)
        )
        post_info = db.fetchall()
        posts[i]['author_id'] = post_info[0]['author_id']
        db.execute(
            'SELECT username, nickname'
            ' FROM user WHERE id=%s',
            (posts[i]['author_id'],)
        )
        user_info = db.fetchall()
        posts[i]['username'] = user_info[0]['username']
        posts[i]['nickname'] = user_info[0]['nickname']
    print(posts)
    return render_template('new_doc.html', posts=posts)
@bp.route('/delete_doc/<int:id>', methods=('GET', 'POST'))
@login_required
def DeleteDoc(id):
    conn, db = get_db()
    db.execute('DELETE FROM post_file WHERE id = %s', (id,))
    conn.commit()
    return redirect(url_for('admin.Doc'))


