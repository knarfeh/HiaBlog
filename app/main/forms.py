#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask_mongoengine.wtf import model_form
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, HiddenField
from wtforms import widgets, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

from . import models


class PostForm(Form):
    title = StringField('Title', validators=[Required()])
    slug = StringField('Slug', validators=[Required()])
    raw = TextAreaField('Content')
    abstract = TextAreaField('Abstract')
    category = StringField('Category')
    tags_str = StringField('Tags')
    post_id = HiddenField('post_id')
    post_type = HiddenField('post_type')

    def validate_slug(self, field):
        posts = models.Post.objects.filter(slug=field.data)
        if posts.count() > 0:
            if not self.post_id.data or str(posts[0].id) != self.post_id.data:
                raise ValidationError('slug already in use')

SuPostForm = model_form(models.Post, exclude=['pub_time', 'update_time', 'content_html', 'category', 'tags'])
