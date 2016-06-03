#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import request, current_app
from blinker import Namespace

from . import models

hiablog_signals = Namespace()
post_visited = hiablog_signals.signal('post-visited')


@post_visited.connect
def on_post_visited(sender, post, **extra):
    tracker = models.Tracker()
    tracker.post = post
    tracker.ip = request.remote_addr
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