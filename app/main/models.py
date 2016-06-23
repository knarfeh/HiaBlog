#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import urllib
import hashlib
import markdown2
import bleach

from flask import url_for
from app.auth.models import User
from app.hia import db
from app.hia.config import HiaBlogSettings


def get_clean_html_content(html_content):
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'hr']
    html_content = bleach.linkify(bleach.clean(html_content, tags=allowed_tags, strip=True))
    return html_content


class Post(db.Document):
    title = db.StringField(max_length=255, default='new blog', required=True)
    slug = db.StringField(max_length=255, required=True, unique=True)
    fix_slug = db.StringField(max_length=255, required=False)
    abstract = db.StringField()
    raw = db.StringField(required=True)
    pub_time = db.DateTimeField()
    update_time = db.DateTimeField()
    content_html = db.StringField(required=True)
    author = db.ReferenceField(User)
    category = db.StringField(max_length=64, default='default')
    tags = db.ListField(db.StringField(max_length=30))
    is_draft = db.BooleanField(default=False)
    post_type = db.StringField(max_length=64, default='post')
    upvotes = db.IntField(default=1)

    def get_absolute_url(self):
        router = {
            'post': url_for('main.post_detail', slug=self.slug, _external=True),
            'page': url_for('main.page_detail', slug=self.slug, _external=True),
        }

        return router[self.post_type]

    def save(self, allow_set_time=False, *args, **kwargs):
        if not allow_set_time:
            now = datetime.datetime.now()
            if not self.pub_time:
                self.pub_time = now
            self.update_time = now

        # self.content_html = self.raw
        self.content_html = markdown2.markdown(self.raw,
                                               extras=['code-friendly', 'fenced-code-blocks', 'tables']).encode('utf-8')
        return super(Post, self).save(*args, **kwargs)

    def set_post_date(self, pub_time, update_time):
        self.pub_time = pub_time
        self.update_time = update_time
        return self.save(allow_set_time=True)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Post %r>' % self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['slug'],
        'ordering': ['-pub_time']
    }


class Draft(db.Document):
    title = db.StringField(max_length=255, default='new blog', required=True)
    slug = db.StringField(max_length=255, required=True, unique=True)
    # fix_slug = db.StringField(max_length=255, required=False)
    abstract = db.StringField()
    raw = db.StringField(required=True)
    pub_time = db.DateTimeField()
    update_time = db.DateTimeField()
    content_html = db.StringField(required=True)
    author = db.ReferenceField(User)
    category = db.StringField(max_length=64, default='default')
    tags = db.ListField(db.StringField(max_length=30))
    is_draft = db.BooleanField(default=True)
    post_type = db.StringField(max_length=64, default='post')

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()
        if not self.pub_time:
            self.pub_time = now
        self.update_time = now
        self.content_html = markdown2.markdown(self.raw,
                                               extras=['code-friendly', 'fenced-code-blocks', 'tables']).encode('utf-8')
        return super(Draft, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Draft %r' % self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['slug'],
        'ordering': ['-update_time']
    }


class Tracker(db.Document):
    post = db.ReferenceField(Post)
    ip = db.StringField()
    user_agent = db.StringField()
    create_time = db.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.create_time:
            self.create_time = datetime.datetime.now()
        return super(Tracker, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.ip

    def __repr__(self):
        return '<Tracker %r>' % self.ip

    meta = {
        'allow_inheritance': True,
        'indexes': ['ip'],
        'ordering': ['-create_time']
    }


class PostStatistics(db.Document):
    post = db.ReferenceField(Post)
    visit_count = db.IntField(default=0)
    verbose_count_base = db.IntField(default=0)

    def __repr__(self):
        return '<PostStatistics %r>' % self.post


COMMENT_STATUS = ('approved', 'pending', 'spam', 'deleted')
GAVATAR_CDN_BASE = HiaBlogSettings['gavatar_cdn_base']
GAVATAR_DEFAULT_IMAGE = HiaBlogSettings['gavatar_default_image']


class Comment(db.Document):
    author = db.StringField(required=True)
    email = db.EmailField(max_length=255)
    homepage = db.URLField()
    post_slug = db.StringField(required=True)
    post_title = db.StringField(default='default article')
    md_content = db.StringField()
    html_content = db.StringField()
    pub_time = db.DateTimeField()
    update_time = db.DateTimeField()
    reply_to = db.ReferenceField('self')
    status = db.StringField(choices=COMMENT_STATUS, default='pending')
    misc = db.StringField()    # If the comment is imported, this field will store something useful
    gavatar_id = db.StringField(default='00000000000')

    def reset_gavatar_id(self):
        if not self.email:
            self.gavatar_id = '00000000000'
            return
        self.gavatar_id = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if self.md_content:
            html_content = markdown2.markdown(self.md_content, extras=['code-friendly', 'fenced-code-blocks',
                                                                       'tables', 'nofollow']).encode('utf-8')
            self.html_content = get_clean_html_content(html_content)

        if not self.pub_time:
            self.pub_time = datetime.datetime.now()

        self.update_time = datetime.datetime.now()
        if self.gavatar_id == '00000000000':
            self.reset_gavatar_id()

        return super(Comment, self).save(*args, **kwargs)

    def get_gavatar_url(self, base_url=GAVATAR_CDN_BASE, img_size=0, default_image_url=None):
        gavatar_url = base_url + self.gavatar_id
        params = {}
        if img_size:
            params['s'] = str(img_size)
        if default_image_url:
            params['d'] = default_image_url

        if params:
            gavatar_url = '{0}?{1}'.format(gavatar_url, urllib.urlencode(params))

        return gavatar_url

    def __unicode__(self):
        return self.md_content[:64]

    meta = {
        'ordering': ['-update_time']
    }

