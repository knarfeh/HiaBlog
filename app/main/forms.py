#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask_mongoengine.wtf import model_form
from flask_wtf import Form
from wtforms import (StringField, PasswordField, BooleanField, TextAreaField, HiddenField, ValidationError, FileField,
                     RadioField)
from wtforms.validators import DataRequired, URL, Length, Email, Optional

from . import models


class PostForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    raw = TextAreaField('Content')
    abstract = TextAreaField('Abstract')
    category = StringField('Category')
    tags_str = StringField('Tags')
    post_id = HiddenField('post_id')
    post_type = HiddenField('post_type')
    from_draft = HiddenField('from_draft')

    def validate_slug(self, field):
        if self.from_draft.data and self.from_draft.data == 'true':
            posts = models.Draft.objects.filter(slug=field.data)
        else:
            posts = models.Post.objects.filter(slug=field.data)
        if posts.count() > 0:
            if not self.post_id.data or str(posts[0].id) != self.post_id.data:
                raise ValidationError('slug already in use')

SuPostForm = model_form(models.Post, exclude=['pub_time',
                                              'update_time', 'content_html', 'category', 'tags', 'post_type'])


class CommentForm(Form):
    email = StringField('* Email', validators=[DataRequired(), Length(1, 128), Email()])
    author = StringField('* Name', validators=[DataRequired(), Length(1, 128)])
    homepage = StringField('Homepage', validators=[URL(), Optional()])
    content = TextAreaField('* Comment <small><span class="label label-info">markdown</span></small>',
                            validators=[DataRequired()])
    comment_id = HiddenField('comment_id')


class SessionCommentForm(Form):
    email = HiddenField('* Email')
    author = HiddenField('* Name')
    homepage = HiddenField('Homepage')
    content = TextAreaField('* Comment', validators=[DataRequired()])
    comment_id = HiddenField('comment_id')


class ImportCommentForm(Form):
    content = TextAreaField('Content')
    json_file = FileField('Json File')
    import_format = RadioField('Import Format', choices=[('text', 'text'), ('file', 'file')], default='text')

