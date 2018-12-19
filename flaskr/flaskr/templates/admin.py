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
from flaskr.blog import get_post

from pprint import pprint

bp = Blueprint('admin', __name__)

def modify_is_top(post_id, is_top):
    conn, db = get_db()
    db.execute(
        'UPDATE post SET is_top = %d'
        ' WHERE id = %s',
        (is_top, post_id)
    )
    conn.commit()

def modify_is_top(post_id, is_fine):
    conn, db = get_db()
    db.execute(
        'UPDATE post SET is_fine = %d'
        ' WHERE id = %s',
        (is_fine, post_id)
    )
    conn.commit()

def modify_is_block(user_id, is_top):
    conn, db = get_db()
    db.execute(
        'UPDATE user SET is_block = %d'
        ' WHERE id = %s',
        (is_top, user_id)
    )
    conn.commit()


def ViewDeleteMember():
    return render_template('new_index.html')
def ViewDeletePost():
    return render_template('new_index.html')



@bp.route('/member', methods=('GET', 'POST'))
@login_required
def member():
    return render_template('new_member.html', post=post)
def DeleteMember(id):
    return render_template('new_member.html', post=post)
def SearchMember(id):
    return render_template('new_member.html', post=post)


@bp.route('/post', methods=('GET', 'POST'))
def post():
     return render_template('new_post.html')
def DeletePost():
    return render_template('new_post.html', post=post)
def SearchPost():
    return render_template('new_post.html', post=post)

@bp.route('/doc', methods=('GET', 'POST'))
def doc():
    return render_template('new_doc.html')
def DeleteDoc():
    return render_template('new_doc.html')
def SearchDoc():
    return render_template('new_doc.html')
