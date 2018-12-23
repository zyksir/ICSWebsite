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
from flaskr.db import get_db
from flaskr.blog import get_post, delete_post, delete_reply

from pprint import pprint

bp = Blueprint('admin', __name__)

def modify_is_top(post_id, is_top):
    conn, db = get_db()
    db.execute(
        'UPDATE post SET is_top = %s'
        ' WHERE id = %s',
        (is_top, post_id)
    )
    conn.commit()

def modify_is_file(post_id, is_fine):
    conn, db = get_db()
    db.execute(
        'UPDATE post SET is_fine = %s'
        ' WHERE id = %s',
        (is_fine, post_id)
    )
    conn.commit()

def modify_is_block(user_id, is_block):
    conn, db = get_db()
    db.execute(
        'UPDATE user SET is_block = %s'
        ' WHERE id = %s',
        (is_block, user_id)
    )
    conn.commit()

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
def member():
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

    return redirect(url_for('admin.member'))
@bp.route('/block_member/<string:id>', methods=('POST', ))
@login_required
def BlockMember(id):
    id = eval(id)
    print(id)
    modify_is_block(id[0], id[1])
    return redirect(url_for('admin.member'))
@bp.route('/search_member/<string:ST>', methods=('GET', 'POST'))
@login_required
def SearchMember(ST):
    s = "%" + ST + "%"
    conn, db = get_db()
    db.execute(
        'SELECT u.id, u.username'
        ' FROM user u'
        ' WHERE u.username LIKE %s'
        ' ORDER BY u.id DESC',
        (s)
    )
    users = db.fetchall()
    pprint(users)
    return json.dumps(users, ensure_ascii=False)


    return redirect(url_for('admin.member'))
    #return render_template('new_member.html', post=post)


@bp.route('/post', methods=('GET', 'POST'))
@login_required
def post():
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
    return redirect(url_for('admin.post'))
@bp.route('/top_post/<string:id>', methods=('GET', 'POST'))
@login_required
def TopPost(id):
    id = eval(id)
    print(id)
    modify_is_top(id[0], id[1])
    return redirect(url_for('admin.post'))
@bp.route('/search_post', methods=('GET', 'POST'))
@login_required
def SearchPost():
    return render_template('new_post.html', post=post)

@bp.route('/doc', methods=('GET', 'POST'))
@login_required
def doc():
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
    return redirect(url_for('admin.doc'))
@bp.route('/search_doc', methods=('GET', 'POST'))
@login_required
def SearchDoc():
    return render_template('new_post.html', post=post)


