#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjdljLJDL08_80jflKzcznv*c'
    MONGODB_SETTINGS = {'DB': 'hia'}

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True

config = {
    'dev': DevConfig,
    'default': DevConfig
}
