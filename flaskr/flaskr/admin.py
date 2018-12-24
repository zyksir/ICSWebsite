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

def modify_is_file(post_id, is_fine):
    post.update({post.is_top: is_fine}).where(post.id == post_id).execute()

def modify_is_block(user_id, is_block):
    user.update({user.is_block: is_block}).where(user.id == user_id).execute()

def SearchPost(ST):
    s = "%" + ST + "%"
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
        tmp_dict['author_id'] = tmp_dict['post']['author']['id']
        files.append(tmp_dict)
    pprint(files)
    return files

def get_admin_home_post():
    return model_to_dict(user.select().where(user.id == 1).get())

def get_Member_post():
    Posts = user.select().where(user.id > 1).order_by(user.created)
    posts = [model_to_dict(Post) for Post in Posts]
    return posts

def get_Post_post():
    posts = []
    Posts = post.select().order_by(post.created)
    for Post in Posts:
        tmp_dict = model_to_dict(Post)
        tmp_dict['nickname'] = tmp_dict['author']['nickname']
        posts.append(tmp_dict)
    return posts

def get_Doc_post():
    Files = post_file.select()
    files = []
    for File in Files:
        tmp_dict = model_to_dict(File)
        tmp_dict['nickname'] = tmp_dict['post']['author']['nickname']
        tmp_dict['username'] = tmp_dict['post']['author']['username']
        tmp_dict['author_id'] = tmp_dict['post']['author']['id']
        files.append(tmp_dict)
    print(files)
    return files

def delete_member(id):
    print("delete No = %d"%(id))
    related_posts = post.select().where(post.author_id == id)
    for related_post in related_posts:
        delete_post(related_post.id)

    reply.delete().where(reply.author_id == id).execute()
    user.delete().where(user.id == id).execute()


def delete_file(id):
    post_file.delete().where(post_file.id == id).execute()


@bp.route('/admin', methods=('GET', 'POST'))
@login_required
def admin_home():
    Post = get_admin_home_post()
    return render_template('new_index.html', post=Post)


@bp.route('/member', methods=('GET', 'POST'))
@login_required
def Member():
    if request.method == 'POST':
        ST = request.form['title']
        posts = SearchMember(ST)
        return render_template('new_member.html', posts=posts)

    mposts = get_Member_post()
    return render_template('new_member.html', posts=mposts)

@bp.route('/delete_member/<int:id>', methods=('POST', ))
@login_required
def DeleteMember(id):
    delete_member(id)
    return redirect(url_for('admin.Member'))
@bp.route('/block_member/<string:id>', methods=('POST', ))
@login_required
def BlockMember(id):
    id = eval(id)
    # print(id)
    modify_is_block(id[0], id[1])
    return redirect(url_for('admin.Member'))

@bp.route('/post', methods=('GET', 'POST'))
@login_required
def Post():
    if request.method == 'POST':
        ST = request.form['title']
        posts = SearchPost(ST)
        return render_template('new_post.html', posts=posts)
    pposts = get_Post_post()
    return render_template('new_post.html', posts=pposts)

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
    files = get_Doc_post()
    return render_template('new_doc.html', posts=files)
@bp.route('/delete_doc/<int:id>', methods=('GET', 'POST'))
@login_required
def DeleteDoc(id):
    delete_file(id)
    return redirect(url_for('admin.Doc'))


