#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

from config import config

db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'accounts.login'


def create_app(config_name):
    app = Flask(__name__,
                template_folder=config[config_name].TEMPLATE_PATH,
                static_folder=config[config_name].STATIC_PATH)

    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    from main.urls import main as main_blueprint, blog_admin as blog_admin_blueprint
    from accounts.urls import accounts as accounts_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(blog_admin_blueprint, url_prefix='/admin')
    app.register_blueprint(accounts_blueprint, url_prefix='/accounts')

    return app