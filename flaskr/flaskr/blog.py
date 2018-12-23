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

from pprint import pprint

bp = Blueprint('blog', __name__)


# check if the post is collected by user
def check_is_collect(user_id, post_id):
    conn, db = get_db()
    db.execute(
        'SELECT c.author_id, c.post_id'
        ' FROM collects c'
        ' WHERE c.author_id = %s ',
        (user_id)
    )
    collects = db.fetchall()
    for acollect in collects:
        if acollect['post_id'] == post_id:
            return True
    return False


# check if the post is collected by user
def check_is_like(user_id, post_id):
    conn, db = get_db()
    db.execute(
        'SELECT l.author_id, l.post_id'
        ' FROM likes l'
        ' WHERE l.author_id = %s ',
        (user_id)
    )
    likes = db.fetchall()
    for alike in likes:
        if alike['post_id'] == post_id:
            return True
    return False


# get num_like from a post
def get_like(post_id):
    conn, db = get_db()
    db.execute(
        'SELECT p.num_like'
        ' FROM  post p'
        ' WHERE p.id = %s ',
        (post_id)
    )
    num_like = db.fetchone()['num_like']
    return num_like


# get num_collect from a post
def get_collect(post_id):
    conn, db = get_db()
    db.execute(
        'SELECT p.num_collect'
        ' FROM  post p'
        ' WHERE p.id = %s ',
        (post_id)
    )
    num_collect = db.fetchone()['num_collect']
    return num_collect


# get a specific post by id
def get_post(id, check_author=True):
    conn, db = get_db()
    db.execute(
        'SELECT p.id, title, body, p.created, author_id, username, p.is_top, p.is_fine'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = db.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# get a post to view by id
def get_view_post(id, check_author=False):
    conn, db = get_db()
    db.execute(
        'SELECT p.id, title, body, p.created, author_id, username, p.is_top, p.is_fine, p.num_view, p.num_reply, p.num_like, p.num_collect, p.num_view'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = db.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    db.execute(
        'SELECT r.id, author_id, body, r.created, username'
        ' FROM reply r JOIN user u ON r.author_id = u.id'
        ' WHERE r.post_id=%s'
        ' ORDER BY created',
        (post['id'])
    )
    posts = db.fetchall()
    post['reply'] = posts

    return post


# delete the reply return the post id of it
def delete_reply(id):
    print("delete reply id = ", id)

    conn, db = get_db()

    db.execute('SET FOREIGN_KEY_CHECKS = 0')
    conn.commit()

    db.execute('SELECT post_id FROM reply r WHERE id=%s', (id,))
    post_id = db.fetchone()['post_id']
    print("post_id = ", post_id)

    db.execute('DELETE FROM reply WHERE id = %s', (id,))
    conn.commit()

    db.execute('SET FOREIGN_KEY_CHECKS = 1')
    conn.commit()

    return post_id


# delete a post by id
def delete_post(id):
    savepath = current_app.config['UPLOAD_FOLDER']
    # get_post(id)
    conn, db = get_db()
    db.execute('SELECT filename, id FROM post_file WHERE post_id=%s', (id,))
    file_list = db.fetchall()
    print("filelist = \n", file_list)
    db.execute('DELETE FROM post_file WHERE post_id=%s', (id,))
    conn.commit()
    print("delete files from MySQL")
    for file in file_list:
        filename = str(file['id']) + "_" + file["filename"]
        filename = os.path.join(savepath, filename)
        print(filename)
        process = subprocess.Popen(["del", filename], shell=True)
        print("%s deleted" % (filename))

    db.execute('SET FOREIGN_KEY_CHECKS = 0')
    conn.commit()

    db.execute('DELETE FROM post WHERE id = %s', (id,))
    conn.commit()

    db.execute('SET FOREIGN_KEY_CHECKS = 1')
    conn.commit()


# index page
@bp.route('/')
def index():
    conn, db = get_db()
    db.execute(
        'SELECT p.id, title, body, p.created, author_id, username, nickname , p.is_top, p.is_fine, p.num_like, p.num_collect, p.num_view'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = db.fetchall()
    posts = sorted(posts, key=lambda p: p['created'], reverse=True)
    # pprint(posts)
    for i, post in enumerate(posts):
        db.execute(
            'SELECT id, post_id, filename, filehash'
            ' FROM post_file WHERE post_id=%s'
            ' ORDER BY created DESC',
            (post['id'],)
        )
        posts[i]['files'] = db.fetchall()

    db.execute(
        'SELECT p.id, title, body, p.created, author_id, username, nickname , p.is_top, p.is_fine, p.hot, p.num_like, p.num_collect, p.num_view'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY hot DESC'
    )
    hots = db.fetchall()

    return render_template('blog/temp_index.html', posts=posts, hots=hots)


# create a new post
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        savepath = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(savepath):
            os.mkdir(savepath)

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()

            db.execute(
                'INSERT INTO post (title, body, author_id, is_top, is_fine)'
                ' VALUES (%s, %s, %s, %s, %s)',
                (title, body, g.user['id'],  0, 0)
            )
            conn.commit()

            db.execute('SELECT LAST_INSERT_ID()')
            post_id = db.fetchone()['LAST_INSERT_ID()']
            # print(post_id)

            db.execute('SELECT author_id, id FROM post WHERE id=%s', (post_id,))
            tmp_list = db.fetchall()
            print(tmp_list)


            for file in request.files.getlist("file"):
                print(type(file))
                print(file.filename)
                file_content = file.read()
                filename = secure_filename(file.filename)
                filehash = generate_password_hash(file_content)

                db.execute(
                    'INSERT INTO post_file (filename, filehash, post_id)'
                    ' VALUES (%s, %s, %s)',
                    (filename, filehash, post_id)
                )
                conn.commit()
                db.execute('SELECT LAST_INSERT_ID()')
                post_file_id = db.fetchone()['LAST_INSERT_ID()']
                file_path = os.path.join(savepath, str(post_file_id)+"_"+filename)
                with open(file_path, "wb") as fw:
                    fw.write(file_content)
                print("Save %s to %s"%(filename, file_path))
            return redirect(url_for('blog.index'))

    return render_template('blog/temp_create.html')


# update a post
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()
            db.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )
            conn.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/temp_update.html', post=post)


# view a post
@bp.route('/ViewPost/<int:id>', methods=('GET', 'POST'))
@login_required
def ViewPost(id):
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()
            db.execute(
                'INSERT INTO reply (body, author_id, post_id)'
                ' VALUES (%s, %s, %s)',
                (body, g.user['id'], id, )
            )
            conn.commit()
            print("insert done!")

            post = get_view_post(id)

            # update the the number of reply
            num_reply = int(post['num_reply']) + 1

            db.execute(
                'UPDATE post SET num_reply = %s'
                ' WHERE id = %s',
                (num_reply, id)
            )
            conn.commit()
            print("num_reply", num_reply)

    post = get_view_post(id)

    # update the the number of views
    num_view = int(post['num_view']) + 1

    conn, db = get_db()
    db.execute(
        'UPDATE post SET num_view = %s'
        ' WHERE id = %s',
        (num_view, id)
    )
    conn.commit()

    is_collect = check_is_collect(g.user['id'], id)
    is_like = check_is_like(g.user['id'], id)

    print("is_like = ", is_like)
    print("is_collect = ", is_collect)

    return render_template('blog/temp_ViewPost.html', post=post, is_collect=is_collect, is_like=is_like)


# delete a reply by id
@bp.route('/DeleteReply/<int:id>', methods=('POST',))
@login_required
def DeleteReply(id):
    post_id = delete_reply(id)
    return redirect(url_for('blog.ViewPost', id=post_id))


@bp.route('/DeletePost/<int:id>', methods=('POST',))
@login_required
def DeletePost(id):
    delete_post(id)
    return redirect(url_for('blog.index'))


# search a keyword ST in titles
def title_search(ST):
    s = "%" + ST + "%"
    conn, db = get_db()
    db.execute(
        'SELECT p.id, p.title'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.title LIKE %s'
        ' ORDER BY p.id DESC',
        (s)
    )
    posts = db.fetchall()
    pprint(posts)
    return posts


# search a keyword ST in titles
@bp.route('/SEARCH/TITLE/<string:ST>')
@login_required
def SEARCH_TITLE(ST):
    posts = title_search(ST)
    return json.dumps(posts, ensure_ascii=False)


# search a keyword ST in users
def user_search(ST):
    s = "%" + ST + "%"
    conn, db = get_db()
    db.execute(
        'SELECT u.id, u.username'
        ' FROM user u'
        ' WHERE u.username LIKE %s OR u.nickname LIKE %s'
        ' ORDER BY u.id DESC',
        (s, s)
    )
    users = db.fetchall()
    pprint(users)
    return users


# search a keyword ST in users
@bp.route('/SEARCH/USER/<string:ST>')
@login_required
def SEARCH_USER(ST):
    users = user_search(ST)
    return json.dumps(users, ensure_ascii=False)


# like a post
@bp.route('/LIKE/<int:id>', methods=('GET', 'POST'))
@login_required
def LIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == False):
        conn, db = get_db()
        print("add like!")
        db.execute(
            'INSERT INTO likes (author_id, post_id)'
            ' VALUES (%s, %s)',
            (user_id, id)
        )
        conn.commit()

        num_like = get_like(id) + 1

        db.execute(
            'UPDATE post SET num_like = %s'
            ' WHERE id = %s',
            (str(num_like), id)
        )
        conn.commit()

        print("num_like = ", num_like)

    return redirect(url_for('blog.ViewPost', id=id))


# collect a post
@bp.route('/COLLECT/<int:id>', methods=('GET', 'POST'))
@login_required
def COLLECT(id):
    user_id = g.user['id']
    print("in collect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == False):
        print("add collect!")
        conn, db = get_db()
        db.execute(
            'INSERT INTO collects (author_id, post_id)'
            ' VALUES (%s, %s)',
            (user_id, id)
        )
        conn.commit()

        num_collect = get_collect(id) + 1

        db.execute(
            'UPDATE post SET num_collect = %s'
            ' WHERE id = %s',
            (str(num_collect), id)
        )
        conn.commit()

        print("num_collect = ", num_collect)

    return redirect(url_for('blog.ViewPost', id=id))


# collect a post
@bp.route('/UNCOLLECT/<int:id>', methods=('GET', 'POST'))
@login_required
def UNCOLLECT(id):
    user_id = g.user['id']
    print("in uncollect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == True):
        print("add uncollect!")
        conn, db = get_db()
        db.execute(
            'DELETE FROM collects WHERE author_id = %s AND post_id = %s',
            (user_id, id)
        )
        conn.commit()

        num_collect = get_collect(id) - 1

        db.execute(
            'UPDATE post SET num_collect = %s'
            ' WHERE id = %s',
            (str(num_collect), id)
        )
        conn.commit()

        print("num_collect = ", num_collect)

    return redirect(url_for('blog.ViewPost', id=id))


# unlike a post
@bp.route('/UNLIKE/<int:id>', methods=('GET', 'POST'))
@login_required
def UNLIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == True):
        conn, db = get_db()
        print("add unlike!")
        db.execute(
            'DELETE FROM likes WHERE author_id = %s AND post_id = %s',
            (user_id, id)
        )
        conn.commit()

        num_like = get_like(id) - 1

        db.execute(
            'UPDATE post SET num_like = %s'
            ' WHERE id = %s',
            (str(num_like), id)
        )
        conn.commit()

        print("num_like = ", num_like)

    return redirect(url_for('blog.ViewPost', id=id))
