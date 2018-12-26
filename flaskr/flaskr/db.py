# -*- coding: utf-8 -*-
# author: zyk
# create a connection to it. Any queries and operations are performed using the connection

import sqlite3
#from flaskext.mysql import MySQL
import pymysql
import os
import click
from flask import current_app, g
from flask.cli import with_appcontext
from peewee import *

if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
    os.mkdir(current_app.config['UPLOAD_FOLDER'])
host = "127.0.0.1"
user = "root"
passwd = 'HWzyk123!@#'
# passwd = 'Daban980624'
<<<<<<< HEAD
passwd = '1998218wrh'
passwd = 'APtx4869'
=======
# passwd = '1998218wrh'
>>>>>>> 32ad770577415b430ea25c0647e5620e65e7c110
database = "sakila"
mydatabase = MySQLDatabase(host=host, user=user, passwd=passwd, database=database, charset="utf8", port=3306)
mydatabase.connect()
# def get_db():
#     if 'db' not in g:
#         user = current_app.config['MYSQL_DATABASE_USER']
#         password = current_app.config['MYSQL_DATABASE_PASSWORD']
#         db = current_app.config['MYSQL_DATABASE_DB']
#         host = current_app.config['MYSQL_DATABASE_HOST']
#         g.conn = pymysql.connect(host, user, password, db)
#         g.db = g.conn.cursor(pymysql.cursors.DictCursor)
#
#     return g.conn, g.db


def close_db(e=None):
    conn = g.pop('conn', None)
    db = g.pop('db', None)

    if db is not None:
        db.close()
    if conn is not None:
        conn.close()


class BaseModel(Model):
    class Meta:
        database = mydatabase

class user(BaseModel):
    id = IntegerField(primary_key=True)
    created = DateTimeField()
    username = CharField(unique=True)
    nickname = CharField()
    password = CharField()
    email = CharField(default="")
    is_block = BooleanField(default=0)

class post(BaseModel):
    id = IntegerField(primary_key=True)
    author = ForeignKeyField(user, backref="author_id1", column_name="author_id")
    author_id = IntegerField()
    num_view = IntegerField(default=0)
    num_reply = IntegerField(default=0)
    num_like = IntegerField(default=0)
    num_collect = IntegerField(default=0)
    hot = DoubleField(default=0.0)
    created = DateTimeField()
    title = TextField()
    body = TextField()
    is_top = BooleanField(default=0)
    is_fine = BooleanField(default=0)

class reply(BaseModel):
    id = IntegerField(primary_key=True)
    author = ForeignKeyField(user, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    author_id = IntegerField()
    post_id = IntegerField()
    created = DateTimeField()
    body = TextField()

class collects(BaseModel):
    id = IntegerField(primary_key=True)
    author = ForeignKeyField(user, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    author_id = IntegerField()
    post_id = IntegerField()

class likes(BaseModel):
    id = IntegerField(primary_key=True)
    author = ForeignKeyField(user, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    author_id = IntegerField()
    post_id = IntegerField()

class post_file(BaseModel):
    id = IntegerField(primary_key=True)
    created = DateTimeField()
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    post_id = IntegerField()
    created = DateTimeField()
    filename = TextField()
    filehash = TextField()

# class post(Model):
#     id = IntegerField()
#     author_id = IntegerField()
#     num_view = IntegerField()
#     num_like = IntegerField()
#     num_collect = IntegerField()
#     num_reply = IntegerField()
#     hot = DoubleField()
#     created = DateTimeField()
#     title = TextField()
#     body = TextField()
#     is_top = BooleanField()
#     is_fine = BooleanField()
#
#     class Meta:
#         database = mydatabase
#
# class user(Model):
#     id = IntegerField()
#     created = DateTimeField()
#     username = CharField()
#     nickname = CharField()
#     password = CharField()
#     email = CharField()
#     is_block = BooleanField()
#
#     class Meta:
#         database = mydatabase
#
#
# class likes(Model):
#     id = IntegerField()
#     author_id = IntegerField()
#     post_id = IntegerField()
#
#     class Meta:
#         database = mydatabase
#
#
# class collects(Model):
#     id = IntegerField()
#     author_id = IntegerField()
#     post_id = IntegerField()
#
#     class Meta:
#         database = mydatabase
#
#
# class reply(Model):
#     id = IntegerField()
#     author_id = IntegerField()
#     post_id = IntegerField()
#     created = DateTimeField()
#     body = TextField()
#
#     class Meta:
#         database = mydatabase
#
#
# class post_file(Model):
#     id = IntegerField()
#     created = DateTimeField()
#     post_id = IntegerField()
#     created = DateTimeField()
#     filename = TextField()
#     filehash = TextField()
#
#     class Meta:
#         database = mydatabase


def init_db():
    print("db.py is going to init_db")
    conn, db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db) # call that function when cleaning up after returning the response
    app.cli.add_command(init_db_command)
