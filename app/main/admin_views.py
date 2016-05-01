#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import request, redirect, render_template, url_for, abort, flash
from flask.views import MethodView
from flask_login import current_user, login_required

from . import models, forms
from accounts.models import User


def get_current_user():
    user = User.objects.get(username=current_user.get_id())
    return user


class AdminIndex(MethodView):
    decorators = [login_required]
    template_name = 'blog_admin/index.html'

    def get(self):
        return render_template(self.template_name)


class PostsList(MethodView):
    decorators = [login_required]
    template_name = 'blog_admin/posts.html'

    def get(self):
        posts = models.Post.objects.all()
        if request.args.get('draft'):
            posts = posts.filter(is_draft=True)
        else:
            posts = posts.filter(is_draft=False)

        return render_template(self.template_name, posts=posts)


class Post(MethodView):
    template_name = 'blog_admin/post.html'

    def get_context(self, slug=None, form=None):
        edit_flag = slug is not None or False
        display_slug = slug if slug else 'slug-value'

        if not form:
            if slug:
                post = models.Post.objects.get_or_404(slug=slug)
                post.post_id = str(post.id)
                post.tags_str = ', '.join(post.tags)
                form = forms.PostForm(obj=post)
            else:
                form = forms.PostForm()

        categories = models.Post.objects.distinct('category')
        tags = models.Post.objects.distinct('tags')
        context = {
            'edit_flag': edit_flag,
            'form': form,
            'display_slug': display_slug,
            'categories': categories,
            'tags': tags
        }
        return context

    def get(self, slug=None, form=None):
        context = self.get_context(slug, form)
        return render_template(self.template_name, **context)

    def post(self, slug=None):
        form = forms.PostForm(obj=request.form)
        if not form.validate():
            return self.get(slug, form)

        if slug:
            post = models.Post.objects.get_or_404(slug=slug)
        else:
            post = models.Post()
            post.author = get_current_user()

        post.title = form.title.data.strip()
        post.slug = form.slug.data.strip()
        post.raw = form.raw.data.strip()
        abstract = form.abstract.data.strip()
        post.abstract = abstract if abstract else post.raw[:140]
        post.category = request.form.get('category')
        post.tags = [tag.strip() for tag in form.tags_str.data.split(',')]


        if request.form.get('publish'):
            post.is_draft = False
            post.save()
            flash('Succeed to publish the post', 'success')
            return redirect(url_for('blog_admin.posts'))

        elif request.form.get('draft'):
            post.is_draft = True
            post.save()
            flash('Succeed to save the draft', 'success')
            return redirect('{0}?draft=true'.format(url_for('blog_admin.posts')))

        return self.get(slug, form)
