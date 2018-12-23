# -*- coding: utf-8 -*-
# author: zyk
# create a connection to it. Any queries and operations are performed using the connection

import sqlite3
#from flaskext.mysql import MySQL
import pymysql
import click
from flask import current_app, g
from flask.cli import with_appcontext
from peewee import *

mydatabase = MySQLDatabase(host="127.0.0.1", user="root", passwd='1998218wrh', database="SAKILA", charset="utf8", port=3306)

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


class post(Model):
    id = IntegerField()
    author_id = IntegerField()
    num_view = IntegerField()
    num_like = IntegerField()
    num_collect = IntegerField()
    num_reply = IntegerField()
    hot = DoubleField()
    created = DateTimeField()
    title = TextField()
    body = TextField()
    is_top = BooleanField()
    is_fine = BooleanField()

    class Meta:
        database = mydatabase


class user(Model):
    id = IntegerField()
    created = DateTimeField()
    username = CharField()
    nickname = CharField()
    password = CharField()
    email = CharField()
    is_block = BooleanField()

    class Meta:
        database = mydatabase


class likes(Model):
    id = IntegerField()
    author_id = IntegerField()
    post_id = IntegerField()

    class Meta:
        database = mydatabase


class collects(Model):
    id = IntegerField()
    author_id = IntegerField()
    post_id = IntegerField()

    class Meta:
        database = mydatabase


class reply(Model):
    id = IntegerField()
    author_id = IntegerField()
    post_id = IntegerField()
    created = DateTimeField()
    body = TextField()

    class Meta:
        database = mydatabase


class post_file(Model):
    id = IntegerField()
    created = DateTimeField()
    post_id = IntegerField()
    created = DateTimeField()
    filename = TextField()
    filehash = TextField()

    class Meta:
        database = mydatabase


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
