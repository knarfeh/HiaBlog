#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from urlparse import urljoin
from flask import request, render_template, abort, g, url_for, flash, redirect, session
from flask import current_app, make_response
from flask_login import current_user

from werkzeug.contrib.atom import AtomFeed
from mongoengine.queryset.visitor import Q

from . import models, signals, forms
from app.auth.models import User
from app.auth.permissions import reader_permission
from app.hia.config import HiaBlogSettings

PER_PAGE = HiaBlogSettings['pagination'].get('per_page', 10)
ARCHIVE_PER_PAGE = HiaBlogSettings['pagination'].get('archive_per_page', 10)


def get_base_data():
    pages = models.Post.objects.filter(post_type='page', is_draft=False)
    blog_meta = HiaBlogSettings['blog_meta']
    data = {'blog_meta': blog_meta, 'pages': pages}
    return data


def list_posts():
    posts = models.Post.objects.filter(post_type='post', is_draft=False).order_by('-pub_time')
    # categories = posts.distinct('category')
    tags = posts.distinct('tags')

    try:
        cur_page = int(request.args.get('page', 1))
    except ValueError:
        cur_page = 1

    cur_category = request.args.get('category')
    cur_tag = request.args.get('tag')
    keywords = request.args.get('keywords')

    if keywords:
        posts = posts.filter(Q(raw__contains=keywords) | Q(title__contains=keywords))

    if cur_category:
        posts = posts.filter(category=cur_category)

    if cur_tag:
        posts = posts.filter(tags=cur_tag)

    # group by aggregate
    category_cursor = models.Post._get_collection().aggregate([{
        '$group': {
            '_id': {
                'category': '$category'
            },
            'name': {
                '$first': '$category'
            },
            'count': {
                '$sum': 1
            },
        }
    }])
    posts = posts.paginate(page=cur_page, per_page=PER_PAGE)

    data = get_base_data()
    data['posts'] = posts
    data['cur_category'] = cur_category
    data['category_cursor'] = category_cursor
    data['cur_tag'] = cur_tag
    data['tags'] = tags
    data['keywords'] = keywords
    return render_template('main/index.html', **data)


def post_detail(slug, post_type='post', fix=False, is_preview=False):
    if is_preview:
        if not g.identity.can(reader_permission):
            abort(401)
        post = models.Draft.objects.get_or_404(slug=slug, post_type=post_type)
    else:
        post = models.Post.objects.get_or_404(slug=slug, post_type=post_type) if not fix else models.Post.objects.get_or_404(fix_slug=slug, post_type=post_type)

    if post.is_draft and current_user.is_anonymous:
        abort(404)

    data = get_base_data()
    data['post'] = post

    if request.form:
        form = forms.CommentForm(obj=request.form)
    else:
        obj = {'author': session.get('author'), 'email': session.get('email'), 'homepage': session.get('homepage'), }
        form = forms.CommentForm(**obj)

    if request.form.get('hia-comment') and form.validate_on_submit():
        hiablog_create_comment(form, post)
        if post_type == 'post':
            url = '{0}#comment'.format(url_for('main.post_detail', slug=slug))
        elif post_type == 'page':
            url = '{0}#comment'.format(url_for('main.page_detail', slug=slug))
        else:
            print(u"post_type:" + str(post_type))
            abort(404)
        msg = u'评论成功, 等待管理者审查通过.'
        flash(msg, 'success')
        return redirect(url)

    data['allow_donate'] = HiaBlogSettings['donation']['allow_donate']
    data['donation_msg'] = HiaBlogSettings['donation']['donation_msg']

    data['allow_comment'] = HiaBlogSettings['blog_comment']['allow_comment']
    if data['allow_comment']:
        comment_type = HiaBlogSettings['blog_comment']['comment_type']
        comment_shortname = HiaBlogSettings['blog_comment']['comment_opt'][comment_type]
        comment_func = get_comment_func(comment_type)
        data['comment_html'] = comment_func(slug, post.title, request.base_url, comment_shortname, form=form) if comment_func else ''

    data['allow_share_article'] = HiaBlogSettings['allow_share_article']

    if not is_preview:
        signals.post_visited.send(current_app._get_current_object(), post=post)

    return render_template('main/post.html', **data)


def post_preview(slug, post_type='post'):
    return post_detail(slug=slug, post_type=post_type, is_preview=True)


def post_detail_general(slug, post_type):
    is_preview = request.args.get('is_preview', 'false')
    is_preview = True if is_preview.lower() == 'true' else False
    return post_detail(slug=slug, post_type=post_type, is_preview=is_preview)


def author_detail(username):
    author = User.objects.get_or_404(username=username)

    posts = models.Post.objects.filter(post_type='post', is_draft=False, author=author).order_by('-pub_time')
    cur_page = request.args.get('page', 1)

    posts = posts.paginate(page=int(cur_page), per_page=ARCHIVE_PER_PAGE)

    data = get_base_data()
    data['user'] = author
    data['posts'] = posts

    return render_template('main/author.html', **data)


def get_comment_func(comment_type):
    comment_func = {
        'hiablog': hiablog_comment,
        'duoshuo': duoshuo_comment,
    }

    return comment_func.get(comment_type)


def hiablog_comment(post_id, post_title, post_url, comment_shortname, form=None, *args, **kwargs):
    template_name = 'main/comments.html'
    comments = models.Comment.objects(post_slug=post_id, status='approved').order_by('pub_time')
    data = {
        'form': form,
        'comments': comments,
        'slug': post_id,
    }
    return render_template(template_name, **data)


def hiablog_create_comment(form, post):
    comment = models.Comment()
    comment.author = form.author.data.strip()
    comment.email = form.email.data.strip()
    comment.homepage = form.homepage.data.strip() or None
    comment.post_slug = post.slug
    comment.post_title = post.title
    comment.md_content = form.content.data.strip()
    comment.save()
    session['author'] = form.author.data.strip()
    session['email'] = form.email.data.strip()
    session['homepage'] = form.homepage.data.strip()


def duoshuo_comment(post_id, post_title, post_url, duoshuo_shortname, *args, **kwargs):
    u"""
    Create duoshuo script by params
    :param duoshuo_shortname:
    :param post_id:
    :param post_title:
    :param post_url:
    :return:
    """
    template_name = 'main/misc/duoshuo.html'
    data = {
        'duoshuo_shortname': duoshuo_shortname,
        'post_id': post_id,
        'post_title': post_title,
        'post_url': post_url,
    }

    return render_template(template_name, **data)


def archive():
    posts = models.Post.objects.filter(post_type='post', is_draft=False).order_by('-pub_time')

    cur_category = request.args.get('category')
    cur_tag = request.args.get('tag')
    cur_page = request.args.get('page', 1)

    if cur_category:
        posts = posts.filter(category=cur_category)

    if cur_tag:
        posts = posts.filter(tags=cur_tag)

    posts = posts.paginate(page=int(cur_page), per_page=ARCHIVE_PER_PAGE)

    data = get_base_data()
    data['posts'] = posts

    return render_template('main/archive.html', **data)


def tweet():
    return render_template('main/tweet.html')


def ticktack():
    return render_template('main/ticktack.html')


def make_external(url):
    return urljoin(request.url_root, url)


def recent_feed():
    feed = AtomFeed('Recent Articles', feed_url=request.url, url=request.url_root)

    posts = models.Post.objects.filter(post_type='post', is_draft=False)[:15]
    for post in posts:
        feed.add(post.title, unicode(post.content_html),
                 content_type='html',
                 author=post.author.username,
                 url=make_external(post.get_absolute_url()),
                 updated=post.update_time,
                 published=post.pub_time)
    return feed.get_response()


def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []

    #########################
    # static pages
    #########################

    ######################
    # Post Pages
    ######################

    posts = models.Post.objects.filter(is_draft=False, post_type='post')
    for post in posts:
        pages.append((post.get_absolute_url(), post.update_time.date().isoformat()))

    ######################
    # Blog-Page Pages
    ######################

    blog_pages = models.Post.objects.filter(is_draft=False, post_type='page')
    for page in blog_pages:
        pages.append((page.get_absolute_url(), page.update_time.date().isoformat()))

    sitemap_xml = render_template('main/sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response




