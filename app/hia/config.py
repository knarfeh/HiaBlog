#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

HiaBlogSettings = {
    'post_types': ('post', 'page'),
    'allow_registration': os.environ.get('HIA_ALLOW_REGISTRATION', 'false').lower() == 'true',
    'allow_su_creation': os.environ.get('HIA_ALLOW_SU_CREATION', 'false').lower() == 'true',
    'allow_donate': os.environ.get('HIA_ALLOW_DONATE', 'true').lower() == 'true',
    'allow_comment': 'true',
    'auto_role': os.environ.get('HIA_AUTO_ROLE', 'reader').lower(),

    'blog_meta': {
        'name': os.environ.get('HIA_NAME').decode('utf8') if os.environ.get('HIA_NAME') else "Frank's Blog",
        'subtitle': os.environ.get('HIA_SUBTITLE').decode('utf8') if os.environ.get('HIA_SUBTITLE') else '',
        'description': os.environ.get('HIA_DESCRIPTION').decode('utf8') if os.environ.get('HIA_DESCRIPTION')
        else u'It’s better to burn out than to fade away',
        'owner': os.environ.get('HIA_OWNER').decode('utf8') if os.environ.get('HIA_OWNER') else 'Frank',
        'keywords': os.environ.get('HIA_KEYWORDS').decode('utf8') if os.environ.get('HIA_KEYWORDS')
        else 'Python, Flask, MongoDB',
        'google_site_verification': os.environ.get('HIA_GOOGLE_SITE_VERIFICATION') or 'TODO',
        'baidu_site_verification': os.environ.get('HIA_BAIDU_SITE_VERIFICATION') or 'TODO',
        'sogou_site_verification': os.environ.get('HIA_SOGOU_SITE_VERIFICATION') or 'TODO',
    },
    'search_engine_submit_urls': {
        'baidu': os.environ.get('HIA_BAIDU_submit_url')
    },
    'pagination': {
        'per_page': int(os.environ.get('per_page', 5)),
        'admin_per_page': int(os.environ.get('admin_per_page', 10)),
        'archive_per_page': int(os.environ.get('admin_per_page', 10)),
    },
    'blog_comment': {
        'allow_comment': os.environ.get('allow_comment', 'true').lower() == 'true',
        'comment_type': os.environ.get('comment_type', 'hiablog').lower(),
        'comment_opt': {
            'duoshuo': 'knarfeh',       # short name of duoshuo
            'hiablog': 'hia-blog',      # short name of hia-blog
        }
    },
    'donation': {
        'allow_donate': os.environ.get('allow_donate', 'true').lower() == 'true',
        'donation_msg': os.environ.get('donation_msg', u'如果觉得我的文章对您有用，请随意打赏。您的支持将鼓励我继续创作！')
    },
    'allow_share_article': os.environ.get('allow_share_article', 'true').lower() == 'true',
    'gavatar_cdn_base': os.environ.get('gavatar_cdn_base', '//cdn.v2ex.com/gravatar/'),
    'gavatar_default_image': os.environ.get('gavatar_default_image', 'http://7xi5vu.com1.z0.glb.clouddn.com/user-avatar.jpg'),
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
    }

config = {
    'dev': DevConfig,
    'prd': PrdConfig,
    'default': DevConfig,
}
