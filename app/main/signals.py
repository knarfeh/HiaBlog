#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import request, current_app
from blinker import Namespace

from . import models, ext
from app.hia.config import HiaBlogSettings

hiablog_signals = Namespace()
post_visited = hiablog_signals.signal('post-visited')
post_published = hiablog_signals.signal('post-published')

search_engine_submit_urls = HiaBlogSettings['search_engine_submit_urls']


@post_visited.connect
def on_post_visited(sender, post, **extra):
    tracker = models.Tracker()
    tracker.post = post

    proxy_list = request.headers.getlist('X-Forwarded-For')
    tracker.ip = request.remote_addr if not proxy_list else proxy_list[0]

    tracker.user_agent = request.headers.get('User-Agent')
    tracker.save()

    try:
        post_statistic = models.PostStatistics.objects.get(post=post)
    except models.PostStatistics.DoesNotExist:
        post_statistic = models.PostStatistics()
        post_statistic.post = post

        from random import randint
        post_statistic.verbose_count_base = randint(500, 5000)

        post_statistic.save()

    post_statistic.modify(inc__visit_count=1)


@post_published.connect
def on_post_pubished(sender, post, **extra):
    post_url = request.host + post.get_absolute_url()
    # print post_url
    baidu_url = search_engine_submit_urls['baidu']
    if baidu_url:
        # print 'Ready to post to baidu'
        res = ext.submit_url_to_baidu(baidu_url, post_url)
        print res.status_code, res.text
    else:
        print 'Not ready to submit urls yet'
