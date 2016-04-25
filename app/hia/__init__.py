#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Flask
from flask_mongoengine import MongoEngine

from config import Config

db = MongoEngine()


def create_app(config_name):
    app = Flask(__name__,
                template_folder=Config.TEMPLATE_PATH,
                static_folder=Config.STATIC_PATH)

    app.config.from_object(Config)

    Config.init_app(app)

    db.init_app(app)

    from main.urls import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
