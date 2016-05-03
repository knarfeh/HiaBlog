#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import markdown2
from flask import url_for


from accounts.models import User
from hia import db


class Post(db.Document):
    title = db.StringField(max_length=255, default='new blog', required=True)
    slug = db.StringField(max_length=255, required=True, unique=True)
    fix_slug = db.StringField(max_length=255, required=False)
    abstract = db.StringField()
    raw = db.StringField(required=True)
    pub_time = db.DateTimeField(required=True)
    update_time = db.DateTimeField(required=True)
    content_html = db.StringField(required=True)
    author = db.ReferenceField(User)
    category = db.StringField(max_length=64, default='default')
    tags = db.ListField(db.StringField(max_length=30))
    is_draft = db.BooleanField(default=False)
    post_type = db.StringField(max_length=64, default='post')


    def get_absolute_url(self):
        return url_for('main.post_detail', slug=self.slug)

    def save(self, allow_set_time=False, *args, **kwargs):
        if not allow_set_time:
            now = datetime.datetime.now()
            if not self.pub_time:
                self.pub_time = now
            self.update_time = now

        # self.content_html = self.raw
        self.content_html = markdown2.markdown(self.raw, extras=['code-friendly', 'fenced-code-blocks']).encode('utf-8')
        return super(Post, self).save(*args, **kwargs)

    def set_post_date(self, pub_time, update_time):
        self.pub_time = pub_time
        self.update_time = update_time
        return self.save(allow_set_time=True)

    def __unicode__(self):
        return self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['slug'],
        'ordering': ['-pub_time']
    }

