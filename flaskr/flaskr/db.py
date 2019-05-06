# -*- coding: utf-8 -*-
# author: zyk
# create a connection to it. Any queries and operations are performed using the connection


from flask import current_app, g
from flask.cli import with_appcontext
from peewee import *
import pymysql


host = "127.0.0.1"
user = "root"
passwd = 'HWzyk123!@#'
# passwd = 'Daban980624'
# passwd = '1998218wrh'
database = "sakila"
mydatabase = MySQLDatabase(host=host, user=user, passwd=passwd, database=database, charset="utf8", port=3306)
mydatabase.connect()


def get_db():
    if 'db' not in g:
        user = current_app.config['MYSQL_DATABASE_USER']
        password = current_app.config['MYSQL_DATABASE_PASSWORD']
        db = current_app.config['MYSQL_DATABASE_DB']
        host = current_app.config['MYSQL_DATABASE_HOST']
        g.conn = pymysql.connect(host, user, password, db)
        g.db = g.conn.cursor(pymysql.cursors.DictCursor)

    return g.conn, g.db

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


def init_app(app):
    return
