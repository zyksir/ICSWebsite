# -*- coding: utf-8 -*-
# author: zyk
#  it will contain the application factory,
#  and it tells Python that
# the flaskr directory should be treated as a package

import os
#om flaskext.mysql import MySQL
from flask import current_app, g
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # mysql = MySQL()
    app.config.from_mapping(    # sets some default configuration that the app will use
         SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    '''app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'Daban980624'
    app.config['MYSQL_DATABASE_DB'] = 'SAKILA'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    app.config['UPLOAD_FOLDER'] = r'E:\temp' '''
    
    # app.config['MYSQL_DATABASE_USER'] = 'root'
    # app.config['MYSQL_DATABASE_PASSWORD'] = 'HWzyk123!@#'
    # app.config['MYSQL_DATABASE_DB'] = 'SAKILA'
    # app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    # app.config['UPLOAD_FOLDER'] = r'E:\system_file'

    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = '1998218wrh'
    app.config['MYSQL_DATABASE_DB'] = 'SAKILA'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    app.config['UPLOAD_FOLDER'] = r'D:\SAKILA'
    
    # mysql.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    print("__init__.py is going to init_app")
    db.init_app(app)

    # XX/auth
    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    # XX/home
    from . import home
    app.register_blueprint(home.bp)

    # XX/user
    from . import user
    app.register_blueprint(user.bp)

    # XX/blog
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app