from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import subprocess
import json
from .db import *

from .auth import login_required

from pprint import pprint

from playhouse.shortcuts import model_to_dict


bp = Blueprint('blog', __name__)


# check if the post is collected by user
def check_is_collect(user_id, post_id):
    try:
        t = collects.select().where(collects.author_id == user_id, collects.post_id == post_id).get()
        return True
    except collects.DoesNotExist:
        return False


# check if the post is collected by user
def check_is_like(user_id, post_id):
    try:
        t = likes.select().where(likes.author_id == user_id, likes.post_id == post_id).get()
        return True
    except likes.DoesNotExist:
        return False


# get num_like from a post
def get_like(post_id):
    num_like = model_to_dict(post.select(post.num_like).where(post.id == post_id).get())['num_like']

    return num_like


# get num_collect from a post
def get_collect(post_id):
    num_collect = model_to_dict(post.select(post.num_collect).where(post.id == post_id).get())['num_collect']

    return num_collect


 # get a specific post by id
def get_post(id, check_author=True):
    try:
        apost = model_to_dict(post.select(post.id, post.title, post.body, post.created, post.author_id, post.is_top, post.is_fine).where(post.id == id).get())
    except post.DoesNotExist:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and apost['author_id'] != g.user['id']:
        abort(403)

    return apost


# get a post to view by id
def get_view_post(id, check_author=False):
    try:
        return_post = model_to_dict(
            post.select(post.id, post.title, post.body, post.created, post.author_id, post.is_top, post.is_fine,
                        post.num_view, post.num_reply, post.num_like, post.num_collect).where(post.id == id).get())
    except post.DoesNotExist:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and return_post['author_id'] != g.user['id']:
        abort(403)

    return_post['username'] = model_to_dict(user.select(user.username).where(user.id == return_post['author_id']).get())['username']

    # pprint(return_post)

    Files = post_file.select().where(post_file.post_id == id)
    return_files = []
    for File in Files:
        return_files.append(model_to_dict(File))

    replys = reply.select(reply.id, reply.author_id, reply.body, reply.created).where(reply.post_id == return_post['id'])
    return_replys = []
    for areply in replys:
        dct_reply = model_to_dict(areply)
        dct_reply['username'] = model_to_dict(user.select(user.username).where(user.id == dct_reply['author_id']).get())['username']
        return_replys.append(dct_reply)

    return_post['file'] = return_files
    return_post['reply'] = return_replys

    return return_post


# delete the reply return the post id of it
def delete_reply(id):
    print("delete reply id = ", id)

    post_id = model_to_dict(reply.select(reply.post_id).where(reply.id == id).get())['post_id']

    print("post_id = ", post_id)

    t = reply.delete().where(reply.id == id)
    t.execute()

    return post_id


# delete a post by id
def delete_post(id):
    savepath = current_app.config['UPLOAD_FOLDER']
    #conn, db = get_db()

    file_list = []
    file_lists = post_file.select(post_file.filename, post_file.id).where(post_file.post_id == id)
    for afile in file_lists:
        file_list.append(model_to_dict(afile))

    print("filelist = \n", file_list)

    t = post_file.delete().where(post_file.post_id == id)
    t.execute()

    print("delete files from MySQL")
    for file in file_list:
        filename = str(file['id']) + "_" + file["filename"]
        filename = os.path.join(savepath, filename)
        print(filename)
        process = subprocess.Popen(["del", filename], shell=True)
        print("%s deleted" % (filename))

    t = reply.delete().where(reply.post_id == id)
    t.execute()

    t = post.delete().where(post.id == id)
    t.execute()


def get_index_info():
    posts = []
    allposts = post.select()
    for apost in allposts:
        dct_apost = model_to_dict(apost)
        this_user = model_to_dict(user.select(user.nickname, user.username).where(user.id == dct_apost['author_id']).get())
        dct_apost['username'] = this_user['username']
        dct_apost['nickname'] = this_user['nickname']

        posts.append(dct_apost)

    posts = sorted(posts, key=lambda p: p['created'], reverse=True)

    for i, apost in enumerate(posts):
        tmp_files = []
        allfiles = post_file.select().where(post_file.post_id == apost['id'])
        for afile in allfiles:
            tmp_files.append(model_to_dict(afile))
        posts[i]['files'] = tmp_files

    hots = []
    allhots = post.select().order_by(post.hot.desc())
    for ahot in allhots:
        dcthot = model_to_dict(ahot)
        auser = model_to_dict(user.select(user.username, user.nickname).where(user.id == dcthot['author_id']).get())
        dcthot['username'] = auser['username']
        dcthot['nickname'] = auser['nickname']
        hots.append(dcthot)

    return posts, hots


# search a keyword ST in titles
def title_search(ST):
    s = "%" + ST + "%"
    t_posts = post.select(post.id, post.title, post.author_id).where(post.title ** s).order_by(post.id.desc())
    posts = []
    for apost in t_posts:
        ta = model_to_dict(apost)
        ta['author_id'] = ta['author']['id']
        ta.pop('author')
        posts.append(ta)

    return posts


# search a keyword ST in users
def user_search(ST):
    s = "%" + ST + "%"

    t_users = user.select(user.id, user.username, user.nickname).where(user.username ** s)

    users = []
    for auser in t_users:
        users.append(model_to_dict(auser))

    return users


def ADD_LIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == False):
        print("add like!")

        t = likes.insert(author_id=user_id, post_id=id)
        t.execute()

        num_like = get_like(id) + 1

        t = post.update(num_like=num_like).where(post.id==id)
        t.execute()

        print("num_like = ", num_like)


def ADD_UNLIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == True):
        print("add unlike!")

        t = likes.delete().where(likes.author_id == user_id, likes.post_id == id)
        t.execute()

        num_like = get_like(id) - 1

        t = post.update(num_like=num_like).where(post.id==id)
        t.execute()

        print("num_like = ", num_like)


def ADD_COLLECT(id):
    user_id = g.user['id']
    print("in collect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == False):
        print("add collect!")

        t = collects.insert(author_id=user_id, post_id=id)
        t.execute()

        num_collect = get_collect(id) + 1

        t = post.update(num_collect=num_collect).where(post.id==id)
        t.execute()

        print("num_collect = ", num_collect)


def ADD_UNCOLLECT(id):
    user_id = g.user['id']
    print("in uncollect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == True):
        print("add uncollect!")

        t = collects.delete().where(collects.author_id == user_id, collects.post_id == id)
        t.execute()

        num_collect = get_collect(id) - 1

        t = post.update(num_collect=num_collect).where(post.id==id)
        t.execute()

        print("num_collect = ", num_collect)


# index page
@bp.route('/')
def index():
    posts, hots = get_index_info()

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
            t = post.insert(title=title, body=body, author_id=g.user['id'], is_top=0, is_fine=0)
            t.execute()

            db.execute('SELECT LAST_INSERT_ID()')
            post_id = db.fetchone()['LAST_INSERT_ID()']

            for file in request.files.getlist("file"):
                print(type(file))
                print(file.filename)
                file_content = file.read()
                filename = secure_filename(file.filename)
                filehash = generate_password_hash(file_content)

                t = post_file.insert(filename=filename, filehash=filehash, post_id=post_id)
                t.execute()

                db.execute('SELECT LAST_INSERT_ID()')
                post_file_id = db.fetchone()['LAST_INSERT_ID()']
                file_path = os.path.join(savepath, str(post_file_id)+"_"+filename)
                with open(file_path, "wb") as fw:
                    fw.write(file_content)
                print("Save %s to %s" % (filename, file_path))
            return redirect(url_for('blog.index'))

    return render_template('blog/temp_create.html')


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
            t = reply.insert(body=body, author_id=g.user['id'], post_id=id)
            t.execute()

            print("insert done!")

            apost = get_view_post(id)

            # update the the number of reply
            num_reply = int(apost['num_reply']) + 1

            t = post.update(num_reply=num_reply).where(post.id == id)
            t.execute()
            print("num_reply", num_reply)

    apost = get_view_post(id)
    pprint(apost)

    # update the the number of views
    num_view = int(apost['num_view']) + 1

    t = post.update(num_view=num_view).where(post.id==id)
    t.execute()

    is_like = check_is_like(g.user['id'], id)
    is_collect = check_is_collect(g.user['id'], id)

    print("is_like = ", is_like)
    print("is_collect = ", is_collect)

    return render_template('blog/temp_ViewPost.html', post=apost, is_collect=is_collect, is_like=is_like)


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
@bp.route('/SEARCH/TITLE/<string:ST>')
@login_required
def SEARCH_TITLE(ST):
    posts = title_search(ST)

    return json.dumps(posts, ensure_ascii=False)


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
    ADD_LIKE(id)

    return redirect(url_for('blog.ViewPost', id=id))


# collect a post
@bp.route('/COLLECT/<int:id>', methods=('GET', 'POST'))
@login_required
def COLLECT(id):
    ADD_COLLECT(id)

    return redirect(url_for('blog.ViewPost', id=id))


# collect a post
@bp.route('/UNCOLLECT/<int:id>', methods=('GET', 'POST'))
@login_required
def UNCOLLECT(id):
    ADD_UNCOLLECT(id)

    return redirect(url_for('blog.ViewPost', id=id))


# unlike a post
@bp.route('/UNLIKE/<int:id>', methods=('GET', 'POST'))
@login_required
def UNLIKE(id):
    ADD_UNLIKE(id)

    return redirect(url_for('blog.ViewPost', id=id))


''' # update a post
@bp.route('/update/<int:id>', methods=('GET', 'POST'))
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

    return render_template('blog/temp_update.html', post=post) '''
