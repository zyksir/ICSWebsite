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

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    conn, db = get_db()
    db.execute(
        'SELECT p.id, title, body, u.created, author_id, username, p.is_top, p.is_fine'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = db.fetchall()
    length = len(posts)
    for i,post in enumerate(posts):
        db.execute(
            'SELECT id, post_id, filename, filehash'
            ' FROM post_file WHERE post_id=%s'
            ' ORDER BY created DESC',
            (post['id'],)
        )
        post['files'] = db.fetchall()

    pprint(posts)

    return render_template('blog/temp_index.html', posts=posts)


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
                (title, body, g.user['id'], 0, 0)
            )
            conn.commit()

            db.execute('SELECT LAST_INSERT_ID()')
            post_id = db.fetchone()['LAST_INSERT_ID()']
            # print(post_id)

            db.execute('SELECT author_id, id FROM post WHERE id=%s', (post_id,))
            tmp_list = db.fetchall()
            print(tmp_list)


            for file in request.files.getlist("file"):
                print(file.filename)
                filename = secure_filename(file.filename)
                filehash = generate_password_hash(file.read())

                db.execute(
                    'INSERT INTO post_file (filename, filehash, post_id)'
                    ' VALUES (%s, %s, %s)',
                    (filename, filehash, post_id)
                )
                conn.commit()
                db.execute('SELECT LAST_INSERT_ID()')
                post_file_id = db.fetchone()['LAST_INSERT_ID()']
                file_path = os.path.join(savepath, str(post_file_id)+"_"+filename)
                file.save(file_path)
                print("Save %s to %s", (filename, file_path))
            return redirect(url_for('blog.index'))

    return render_template('blog/temp_create.html')


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


def get_view_post(id, check_author=False):
    conn, db = get_db()
    db.execute(
        'SELECT p.id, title, body, p.created, author_id, username, p.is_top, p.is_fine'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (id,)
    )
    post = db.fetchone()
    # pprint(post)

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)


    db.execute(
        'SELECT r.id, author_id, body, r.created, username'
        ' FROM reply r JOIN user u ON r.author_id = u.id'
        ' WHERE r.post_id=%s'
        ' ORDER BY created DESC',
        (post['id'])
    )
    posts = db.fetchall()
    post['reply'] = posts
    # pprint(post)

    #print(type(post))
    #pprint(post)

    return post
    

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


@bp.route('/<int:id>/ViewPost', methods=('GET', 'POST'))
@login_required
def ViewPost(id):
    #pprint(post)

    if request.method == 'POST':
        # title = request.form['title']
        body = request.form['body']
        error = None

        print(id)

        #if not title:
        #    error = 'Title is required.'

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

            #post = get_view_post(id)
            #render_template('blog/ViewPost.html', post=post)

    post = get_view_post(id)
    return render_template('blog/temp_ViewPost.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    savepath = current_app.config['UPLOAD_FOLDER']
    get_post(id)
    conn, db = get_db()
    db.execute('SELECT filename, id FROM post_file WHERE post_id=%s', (id, ))
    file_list = db.fetchall()
    print(file_list)
    db.execute('DELETE FROM post_file WHERE post_id=%s', (id,))
    conn.commit()
    print("delete files from MySQL")
    for file in file_list:
        filename = str(file['id'])+"_"+file["filename"]
        filename = os.path.join(savepath, filename)
        print(filename)
        process = subprocess.Popen(["del", filename], shell=True)
        print("%s deleted"%(filename))

    db.execute('DELETE FROM post WHERE id = %s', (id,))
    conn.commit()
    return redirect(url_for('blog.index'))