#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

HiaBlogSettings = {
    'post_types': ('post', 'page'),
    'allow_registration': os.environ.get('allow_registration', 'false').lower() == 'true',
    'allow_su_creation': os.environ.get('allow_su_creation', 'false').lower() == 'true',
    'allow_donate': os.environ.get('allow_donate', 'true').lower() == 'true',
    'allow_comment': 'true',
    'auto_role': os.environ.get('auto_role', 'reader').lower(),

    'blog_meta': {
        'name': os.environ.get('name').decode('utf8') if os.environ.get('name') else "Frank's Blog",
        'subtitle': os.environ.get('subtitle').decode('utf8') if os.environ.get('subtitle') else '',
        'description': os.environ.get('description').decode('utf8') if os.environ.get('description') else u'It’s better to burn out than to fade away',
        'owner': os.environ.get('owner').decode('utf8') if os.environ.get('owner') else 'Frank',
        'keywords': os.environ.get('keywords').decode('utf8') if os.environ.get('keywords')
        else 'Python, Flask, MongoDB',

        'google_site_verification': os.environ.get('google_site_verification') or '12345678',
        'baidu_site_verification': os.environ.get('baidu_site_verification') or '87654321',

    },
    'pagination': {
        'per_page': int(os.environ.get('per_page', 5)),
        'admin_per_page': int(os.environ.get('admin_per_page', 10)),
        'archive_per_page': int(os.environ.get('admin_per_page', 10)),
    },
    'blog_comment': {
        'allow_comment': os.environ.get('allow_comment', 'true').lower() == 'true',
        'comment_type': os.environ.get('comment_type', 'duoshuo').lower(),
        'comment_opt': {
            'duoshuo': 'knarfeh',     # shotname of duoshuo
        }
    },
    'donation': {
        'allow_donate': os.environ.get('allow_donate', 'true').lower() == 'true',
        'donation_msg': os.environ.get('donation_msg', u'如果觉得我的文章对您有用，请随意打赏。您的支持将鼓励我继续创作！')
    },

    'allow_share_article': os.environ.get('allow_share_article', 'true').lower() == 'true',
}


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


class PrdConfig(Config):
    # DEBUG = False
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    MONGODB_SETTINGS = {
            'db': 'HiaBlog',
            'host': os.environ.get('MONGO_HOST') or 'localhost',
            # 'port': 12345
    }

config = {
    'dev': DevConfig,
    'prd': PrdConfig,
    'default': DevConfig,
}
