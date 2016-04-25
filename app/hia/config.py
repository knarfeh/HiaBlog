#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates').replace('\\', '/')

# print BASE_DIR


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjdljLJDL08_80jflKzcznv*c'
    MONGODB_SETTINGS = {'DB': 'hia'}

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates').replace('\\', '/')
    STATIC_PATH = os.path.join(BASE_DIR, 'static').replace('\\', '/')

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True

config = {
    'dev': DevConfig,
    'default': DevConfig
}
