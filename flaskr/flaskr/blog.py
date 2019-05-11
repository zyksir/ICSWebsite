from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for, current_app,send_from_directory
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
    conn, db = get_db()
    t = db.execute(
        "SELECT * FROM COLLECTS WHERE author_id=%s AND post_id=%s", (user_id, post_id)
    )
    return t > 0
    try:
        t = collects.select().where(collects.author_id == user_id, collects.post_id == post_id).get()
        return True
    except collects.DoesNotExist:
        return False


# check if the post is collected by user
def check_is_like(user_id, post_id):
    conn, db = get_db()
    t = db.execute(
        "SELECT * FROM likes WHERE author_id=%s AND post_id=%s", (user_id, post_id)
    )
    return t > 0
    try:
        t = likes.select().where(likes.author_id == user_id, likes.post_id == post_id).get()
        return True
    except likes.DoesNotExist:
        return False


# get num_like from a post
def get_like(post_id):
    conn, db = get_db()
    db.execute(
        "SELECT num_like FROM post WHERE id=%s", (post_id)
    )
    num_like = db.fetchone()["num_like"]
    # num_like = model_to_dict(post.select(post.num_like).where(post.id == post_id).get())['num_like']

    return num_like


# get num_collect from a post
def get_collect(post_id):
    conn, db = get_db()
    db.execute(
        "SELECT num_collect FROM post WHERE id=%s", (post_id)
    )
    num_collect = db.fetchone()["num_collect"]
    # num_collect = model_to_dict(post.select(post.num_collect).where(post.id == post_id).get())['num_collect']

    return num_collect


 # get a specific post by id
def get_post(id, check_author=True):
    conn, db = get_db()
    num = db.execute(
        "SELECT * FROM post WHERE id=%s", (id)
    )
    if num == 0:
        abort(404, "Post id {0} doesn't exist.".format(id))
    else:
        apost = db.fetchone()
    # try:
    #     apost = model_to_dict(post.select(post.id, post.title, post.body, post.created, post.author_id, post.is_top, post.is_fine).where(post.id == id).get())
    # except post.DoesNotExist:
    #     abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and apost['author_id'] != g.user['id']:
        abort(403)

    return apost


# get a post to view by id
def get_view_post(id, check_author=False):
    conn, db = get_db()
    num = db.execute(
        "SELECT post.*, user.username "
        "FROM post INNER JOIN user ON user.id=post.author_id WHERE post.id=%s", (id)
    )
    if num == 0:
        abort(404, "Post id {0} doesn't exist.".format(id))
    else:
        return_post = db.fetchone()
        # print(return_post)

       # try:
    #     return_post = model_to_dict(
    #         post.select(post.id, post.title, post.body, post.created, post.author_id, post.is_top, post.is_fine,
    #                     post.num_view, post.num_reply, post.num_like, post.num_collect).where(post.id == id).get())
    # except post.DoesNotExist:
    #     abort(404, "Post id {0} doesn't exist.".format(id))
    #
    # if check_author and return_post['author_id'] != g.user['id']:
    #     abort(403)
    #
    # return_post['username'] = model_to_dict(user.select(user.username).where(user.id == return_post['author_id']).get())['username']
    # pprint(return_post)

    db.execute(
        "SELECT * FROM post_file WHERE post_id = %s", (id)
    )
    return_files = db.fetchall()
    # Files = post_file.select().where(post_file.post_id == id)
    # return_files = []
    # for File in Files:
    #     return_files.append(model_to_dict(File))

    db.execute(
        "SELECT user.username, reply.* "
        "FROM reply INNER JOIN user ON user.id=reply.author_id "
        "WHERE reply.post_id=%s", (return_post['id'])
    )
    return_replys = db.fetchall()
    # replys = reply.select(reply.id, reply.author_id, reply.body, reply.created).where(reply.post_id == return_post['id'])
    # return_replys = []
    # for areply in replys:
    #     dct_reply = model_to_dict(areply)
    #     dct_reply['username'] = model_to_dict(user.select(user.username).where(user.id == dct_reply['author_id']).get())['username']
    #     return_replys.append(dct_reply)

    return_post['file'] = return_files
    return_post['reply'] = return_replys

    return return_post


# delete the reply return the post id of it
def delete_reply(id):
    print("delete reply id = ", id)

    conn, db = get_db()
    db.execute(
        "SELECT post_id FROM reply WHERE id=%s", (id)
    )
    post_id = db.fetchall()["post_id"]
    # post_id = model_to_dict(reply.select(reply.post_id).where(reply.id == id).get())['post_id']

    print("post_id = ", post_id)
    db.execute(
        "DELETE FROM reply WHERE id=%s", (id)
    )
    conn.commit()
    # t = reply.delete().where(reply.id == id)
    # t.execute()

    # update the the number of reply
    # db.execute(
    #     "SELECT num_reply FROM post WHERE id=%s", (post_id)
    # )
    # apost = db.fetchone()
    #
    # # apost = model_to_dict(post.select(post.num_reply).where(post.id == post_id).get())
    # num_reply = int(apost['num_reply']) - 1
    #
    # db.execute(
    #     "UPDATE num_reply SET num_reply=%s WHERE id=%s", (num_reply, post_id)
    # )
    # conn.commit()
    # t = post.update(num_reply=num_reply).where(post.id == post_id)
    # t.execute()
    # print("num_reply", num_reply)

    return post_id


# delete a post by id
def delete_post(id):
    savepath = current_app.config['UPLOAD_FOLDER']
    conn, db = get_db()

    db.execute(
        "CALL delete_post(%s)", (id)
    )
    file_list = db.fetchall()
    print(file_list)
    conn.commit()
    # file_list = []
    # file_lists = post_file.select(post_file.filename, post_file.id).where(post_file.post_id == id)
    # for afile in file_lists:
    #     file_list.append(model_to_dict(afile))
    # db.execute(
    #     "SELECT filename, id FROM post_file WHERE post_id = %s", (id)
    # )
    # file_list = db.fetchall()
    # print("filelist = \n", file_list)

    # db.execute(
    #     "DELETE FROM collects WHERE post_id=%s", (id)
    # )
    # conn.commit()
    # t = collects.delete().where(collects.post_id == id)
    # t.execute()

    # db.execute(
    #     "DELETE FROM likes WHERE post_id=%s", (id)
    # )
    # conn.commit()
    # t = likes.delete().where(likes.post_id == id)
    # t.execute()

    # db.execute(
    #     "DELETE FROM post_file WHERE post_id=%s", (id)
    # )
    # conn.commit()
    # t = post_file.delete().where(post_file.post_id == id)
    # t.execute()

    print("delete files from MySQL")
    for file in file_list:
        filename = str(file['id']) + "_" + file["filename"]
        filename = os.path.join(savepath, filename)
        print(filename)
        process = subprocess.Popen(["del", filename], shell=True)
        print("%s deleted" % (filename))

    # db.execute(
    #     "DELETE FROM reply WHERE post_id=%s", (id)
    # )
    # conn.commit()
    # t = reply.delete().where(reply.post_id == id)
    # t.execute()

    # db.execute(
    #     "DELETE FROM post WHERE id=%s", (id)
    # )
    # conn.commit()
    # t = post.delete().where(post.id == id)
    # t.execute()


def get_index_info():
    conn, db = get_db()
    db.execute(
        "SELECT post.*, user.nickname, user.username "
        "FROM post INNER JOIN user ON post.author_id = user.id "
        "ORDER BY post.created DESC"
    )
    posts = db.fetchall()

    # posts = []
    # allposts = post.select()
    # for apost in allposts:
    #     dct_apost = model_to_dict(apost)
    #     this_user = model_to_dict(user.select(user.nickname, user.username).where(user.id == dct_apost['author_id']).get())
    #     dct_apost['username'] = this_user['username']
    #     dct_apost['nickname'] = this_user['nickname']
    #
    #     posts.append(dct_apost)
    # posts = sorted(posts, key=lambda p: p['created'], reverse=True)

    for i, apost in enumerate(posts):
        db.execute(
            "SELECT * FROM post_file WHERE post_id=%s", (apost["id"])
        )
        posts[i]['files'] = db.fetchall()
        # tmp_files = []
        # allfiles = post_file.select().where(post_file.post_id == apost['id'])
        # for afile in allfiles:
        #     tmp_files.append(model_to_dict(afile))
        # posts[i]['files'] = tmp_files

    db.execute(
        "SELECT post.*, user.username, user.nickname "
        "FROM user INNER JOIN post ON user.id=post.author_id "
        "ORDER BY post.hot DESC"
    )
    hots = db.fetchall()
    # hots = []
    # allhots = post.select().order_by(post.hot.desc())
    # for ahot in allhots:
    #     dcthot = model_to_dict(ahot)
    #     auser = model_to_dict(user.select(user.username, user.nickname).where(user.id == dcthot['author_id']).get())
    #     dcthot['username'] = auser['username']
    #     dcthot['nickname'] = auser['nickname']
    #     hots.append(dcthot)
    session['hots'] = hots

    return posts, hots


# search a keyword ST in titles
def title_search(ST):
    s = "%" + ST + "%"
    conn, db = get_db()
    db.execute(
        "SELECT post.*, user.username, user.nickname "
        "FROM user INNER JOIN post ON user.id=post.author_id "
        "WHERE post.title ** %s "
        "ORDER BY post.id DESC", (s)
    )
    posts = db.fetchall()
    # t_posts = post.select().where(post.title ** s).order_by(post.id.desc())
    # posts = []
    # for apost in t_posts:
    #     ta = model_to_dict(apost)
    #     this_user = model_to_dict(user.select(user.nickname, user.username).where(user.id == ta['author_id']).get())
    #     ta['username'] = this_user['username']
    #     ta['nickname'] = this_user['nickname']
    #     # pprint(ta)
    #     ta['author_id']# = ta['author']['id']
    #     # ta.pop('author')
    #     posts.append(ta)

    # print("posts")
    # pprint(posts)

    return posts


# search a keyword ST in users
def user_search(ST):
    s = "%" + ST + "%"
    conn, db = get_db()
    db.execute(
        "SELECT id, username, nickname"
        "FROM user WHERE user.username ** %s", (s)
    )
    users = db.fetchall()
    # t_users = user.select(user.id, user.username, user.nickname).where(user.username ** s)
    #
    # users = []
    # for auser in t_users:
    #     users.append(model_to_dict(auser))

    return users


def ADD_LIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == False):
        print("add like!")
        conn, db = get_db()
        db.execute(
            "INSERT INTO likes (author_id, post_id) VALUE (%s, %s)", (user_id, id)
        )
        conn.commit()
        # t = likes.insert(author_id=user_id, post_id=id)
        # t.execute()

        # num_like = get_like(id) + 1
        #
        # db.execute(
        #     "UPDATE post SET num_like=%s WHERE post.id=%s", (num_like, id)
        # )
        # db.execute(
        #     "UPDATE post SET num_like=num_like+1 WHERE post.id=%s", (id)
        # )
        # conn.commit()
        # t = post.update(num_like=num_like).where(post.id==id)
        # t.execute()

        # print("num_like = ", num_like)


def ADD_UNLIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == True):
        print("add unlike!")

        conn, db = get_db()
        db.execute(
            "DELETE FROM likes WHERE author_id=%s and post_id=%s", (user_id, id)
        )
        conn.commit()
        # t = likes.delete().where(likes.author_id == user_id, likes.post_id == id)
        # t.execute()

        # num_like = get_like(id) - 1
        #
        # db.execute(
        #     "UPDATE post SET num_like=%s WHERE post.id=%s", (num_like, id)
        # )
        # conn.commit()
        # t = post.update(num_like=num_like).where(post.id==id)
        # t.execute()

        # print("num_like = ", num_like)


def ADD_COLLECT(id):
    user_id = g.user['id']
    print("in collect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == False):
        print("add collect!")
        conn, db = get_db()
        db.execute(
            "INSERT INTO collects (author_id, post_id) VALUE (%s, %s)", (user_id, id)
        )
        conn.commit()
        # t = collects.insert(author_id=user_id, post_id=id)
        # t.execute()

        # num_collect = get_collect(id) + 1
        #
        # db.execute(
        #     "UPDATE post SET num_collect=%s WHERE post.id=%s", (num_collect, id)
        # )
        # conn.commit()
        # t = post.update(num_collect=num_collect).where(post.id==id)
        # t.execute()

        # print("num_collect = ", num_collect)


def ADD_UNCOLLECT(id):
    user_id = g.user['id']
    print("in uncollect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == True):
        print("add uncollect!")
        conn, db = get_db()
        db.execute(
            "DELETE FROM collects WHERE author_id=%s and post_id=%s", (user_id, id)
        )
        conn.commit()
        # t = collects.delete().where(collects.author_id == user_id, collects.post_id == id)
        # t.execute()

        # num_collect = get_collect(id) - 1
        #
        # db.execute(
        #     "UPDATE post SET num_collect=%s WHERE post.id=%s", (num_collect, id)
        # )
        # conn.commit()
        # t = post.update(num_collect=num_collect).where(post.id==id)
        # t.execute()

        # print("num_collect = ", num_collect)


def SAVE_FILES(file_list, savepath, post_id):
    for file in file_list:
        print(type(file))
        print(file.filename)
        file_content = file.read()
        filename = secure_filename(file.filename)
        filehash = generate_password_hash(file_content)

        conn, db = get_db()
        post_file_id = db.execute(
            "INSERT INTO post_file (filename, filehash, post_id) VALUE (%s, %s, %s)", (filename, filehash, post_id)
        )
        conn.commit()
        # t = post_file.insert(filename=filename, filehash=filehash, post_id=post_id)
        # post_file_id = t.execute()

        file_path = os.path.join(savepath, str(post_file_id) + "_" + filename)
        with open(file_path, "wb") as fw:
            fw.write(file_content)
        print("Save %s(file id:%s) to %s" % (filename, str(post_file_id), file_path))


# index page
@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        ST = request.form.get("searchkeywords",type=str,default=None)
        # posts = title_search(ST)
        return redirect(url_for('blog.SEARCH_TITLE', ST=ST))

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
            db.execute(
                "INSERT INTO post (title, body, author_id, is_top, is_fine) "
                "VALUE "
                "(%s, %s, %s, %s, %s)", (title, body, g.user["id"], 0, 0)
            )
            conn.commit()
            db.execute(
                "SELECT LAST_INSERT_ID()"
            )
            post_id = db.fetchone()["LAST_INSERT_ID()"]
            # t = post.insert(title=title, body=body, author_id=g.user['id'], is_top=0, is_fine=0)
            # post_id = t.execute()
            print(post_id)

            SAVE_FILES(request.files.getlist("file"), savepath, post_id)
            return redirect(url_for('blog.index'))

    return render_template('blog/temp_create.html')


# view a post
@bp.route('/ViewPost/<int:id>', methods=('GET', 'POST'))
def ViewPost(id):
    conn, db = get_db()
    if request.method == 'POST':
        body = request.form.get("body", type=str, default=None)
        ST = request.form.get("searchkeywords", type=str, default=None)
        Filename = request.form.get("file", type=str, default=None)
        if body:
            error = None
        if ST:
            posts = title_search(ST)
            return redirect(url_for('blog.SEARCH_TITLE', ST=ST))
            return render_template('blog/temp_SearchResult.html', posts=posts)
            error = None

        if error is not None:
            flash(error)
        else:
            db.execute(
                "INSERT INTO reply (body, author_id, post_id) VALUE (%s, %s, %s)", (body, g.user['id'], id)
            )
            conn.commit()
            # t = reply.insert(body=body, author_id=g.user['id'], post_id=id)
            # t.execute()

            print("insert done!")

            # apost = get_view_post(id)

            # update the the number of reply
            # num_reply = int(apost['num_reply']) + 1
            #
            # db.execute(
            #     "UPDATE post SET num_reply=%s WHERE id=%s", (num_reply, id)
            # )
            # conn.commit()
            # t = post.update(num_reply=num_reply).where(post.id == id)
            # t.execute()
            # print("num_reply", num_reply)

    apost = get_view_post(id)
    pprint(apost)

    # update the the number of views
    num_view = int(apost['num_view']) + 1

    db.execute(
        "UPDATE post SET num_view=%s WHERE id=%s", (num_view, id)
    )
    conn.commit()
    # t = post.update(num_view=num_view).where(post.id==id)
    # t.execute()
    is_like = None
    is_collect = None
    if g.user:
        is_like = check_is_like(g.user['id'], id)
        is_collect = check_is_collect(g.user['id'], id)
        print("is_like = ", is_like)
        print("is_collect = ", is_collect)

    return render_template('blog/temp_ViewPost.html', post=apost, is_collect=is_collect, is_like=is_like, hots=session['hots'])


def CHECK_DOWNLOADFILE(post_file_id, filename):
    with open(filename, "rb") as f:
        content = f.read()
        conn, db = get_db()
        db.execute(
            "SELECT filehash FROM post_file WHERE id=%s", (post_file_id)
        )
        filehash = db.fetchone()["filehash"]
        # filehash = model_to_dict(post_file.select().where(post_file.id == post_file_id).get())['filehash']
        if not check_password_hash(filehash, content):
            error = "文件已被修改"
            return error


@bp.route('/DownloadFile/<string:filename>', methods=('POST', ))
def DownloadFile(filename):
    print(filename)
    tmp_list = eval(filename)
    filename = tmp_list[0]
    post_file_id = tmp_list[1]
    post_id = tmp_list[2]
    filename = str(post_file_id)+"_"+filename
    error = CHECK_DOWNLOADFILE(post_file_id, os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    if error:
        flash(error)
        return redirect(url_for("blog.ViewPost", id=post_id))

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


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
@bp.route('/SEARCH/TITLE/<string:ST>', methods=('GET','POST'))
@login_required
def SEARCH_TITLE(ST):
    if request.method == 'POST':
        ST = request.form.get("searchkeywords", type=str,default=None)
        # posts = title_search(ST)
        return redirect(url_for('blog.SEARCH_TITLE', ST=ST))
    posts = title_search(ST)
    users = user_search(ST)
    return render_template('blog/temp_SearchResult.html', posts=posts, users=users)


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
