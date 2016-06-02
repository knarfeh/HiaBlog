#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from urlparse import urljoin
from datetime import datetime, timedelta
from flask import request, redirect, render_template, url_for, abort, flash
from flask import current_app, make_response
from flask.views import MethodView
from flask_login import login_required, current_user

from werkzeug.contrib.atom import AtomFeed
from mongoengine.queryset.visitor import Q


from . import models
from app.accounts.models import User
from app.hia.config import HiaBlogSettings

PER_PAGE = HiaBlogSettings['pagination'].get('per_page', 10)
ARCHIVE_PER_PAGE = HiaBlogSettings['pagination'].get('archive_per_page', 10)


def get_base_data():
    pages = models.Post.objects.filter(post_type='page', is_draft=False)
    blog_meta = HiaBlogSettings['blog_meta']
    data = {'blog_meta': blog_meta, 'pages': pages}
    return data


def index():
    return 'Hello'


def list_posts():
    posts = models.Post.objects.filter(post_type='post', is_draft=False).order_by('-pub_time')
    # categories = posts.distinct('category')
    tags = posts.distinct('tags')
    cur_category = request.args.get('category')
    cur_tag = request.args.get('tag')
    cur_page = request.args.get('page', 1)
    keywords = request.args.get('keywords')

    if keywords:
        # posts = posts.filter(raw__contains=keywords )
        posts = posts.filter(Q(raw__contains=keywords) | Q(title__contains=keywords))

    if cur_category:
        posts = posts.filter(category=cur_category)

    if cur_tag:
        posts = posts.filter(tags=cur_tag)

    posts = posts.paginate(page=int(cur_page), per_page=PER_PAGE)

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

    data = get_base_data()
    data['posts'] = posts
    data['cur_category'] = cur_category
    data['category_cursor'] = category_cursor
    data['cur_tag'] = cur_tag
    data['tags'] = tags
    data['keywords'] = keywords

    return render_template('main/index.html', **data)


def post_detail(slug, post_type='post', fix=False):
    post = models.Post.objects.get_or_404(slug=slug, post_type=post_type) if not fix else models.Post.objects.get_or_404(fix_slug=slug, post_type=post_type)
    if post.is_draft and current_user.is_anonymous:
        abort(404)

    data = get_base_data()
    data['post'] = post
    data['allow_donate'] = HiaBlogSettings['donation']['allow_donate']
    data['donation_msg'] = HiaBlogSettings['donation']['donation_msg']

    data['allow_comment'] = HiaBlogSettings['blog_comment']['allow_comment']
    if data['allow_comment']:
        comment_type = HiaBlogSettings['blog_comment']['comment_type']
        comment_shortname = HiaBlogSettings['blog_comment']['comment_opt']['duoshuo']
        comment_func = get_comment_func(comment_type)
        data['comment_html'] = comment_func(comment_shortname, slug, post.title, request.base_url) if comment_func else ''

    data['allow_share_article'] = HiaBlogSettings['allow_share_article']

    return render_template('main/post.html', **data)


def author_detail(username):
    author = User.objects.get_or_404(username=username)

    posts = models.Post.objects.filter(post_type='post', is_draft=False, author=author).order_by('-pub_time')
    cur_page = request.args.get('page', 1)

    posts = posts.paginate(page=int(cur_page), per_page=ARCHIVE_PER_PAGE)

    data = get_base_data()
    data['user'] = author
    data['posts'] = posts
    # data['category_cursor'] = category_cursor
    # data['cur_tag'] = cur_tag
    # data['tags'] = tags
    # data['keywords'] = keywords

    return render_template('main/author.html', **data)



def get_comment_func(comment_type):
    if comment_type == 'duoshuo':
        return duoshuo_comment
    else:
        return None


def duoshuo_comment(duoshuo_shortname, post_id, post_title, post_url):
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


# def jiathis_share():
#     u"""
#     Create jiathis script by params
#     :return:
#     """
#     template_name = 'main/misc/jiathis_share.html'
#     return render_template(template_name)

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



def make_external(url):
    return urljoin(request.url_root, url)


def recent_feed():
    feed = AtomFeed('Recent Articles', feed_url=request.url, url=request.url_root)

    posts = models.Post.objects.filter(post_type='post', is_draft=False)[:15]
    for post in posts:
        # return post.get_absolute_url()
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

    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()

    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            pages.append(
                         [rule.rule, ten_days_ago]
                         )

    ## user model pages
    # users=User.query.order_by(User.modified_time).all()
    # for user in users:
    #     url=url_for('user.pub',name=user.name)
    #     modified_time=user.modified_time.date().isoformat()
    #     pages.append([url,modified_time])

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




