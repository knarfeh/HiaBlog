#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjdljLJDL08_80jflKzcznv*c'
    MONGODB_SETTINGS = {'DB': 'hia'}

    TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates').replace('\\', '/')
    STATIC_PATH = os.path.join(BASE_DIR, 'static').replace('\\', '/')

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True


HiaBlogSettings = {
    'allow_registration': os.environ.get('allow_registration', 'false').lower() == 'true',
    'blog_meta': {
        'name': os.environ.get('name') or 'Hia Blog',
        'subtitle': os.environ.get('subtitle') or '',
        'description': os.environ.get('description') or u'黑客态度 侠义精神',
        'owner': os.environ.get('owner') or 'knarfef',
        # 'keywords': os.environ.get('keywords') or 'python,django,flask,docker,MongoDB',
        'google_site_verification': os.environ.get('google_site_verification') or '12345678',
        'baidu_site_verification': os.environ.get('baidu_site_verification') or '87654321',

    },

    'pagination': {
        'per_page': int(os.environ.get('per_page', 5)),
        'admin_per_page': int(os.environ.get('admin_per_page', 10)),

    },


}


class PrdConfig(Config):
    # DEBUG = False
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    MONGODB_SETTINGS = {
            'db': 'OctBlog',
            'host': os.environ.get('MONGO_HOST') or 'localhost',
            # 'port': 12345
    }

config = {
    'dev': DevConfig,
    'prd': PrdConfig,
    'default': DevConfig,
}
