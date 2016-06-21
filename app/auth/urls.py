#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Blueprint
from . import views
from app.main import errors

auth = Blueprint('auth', __name__)

auth.add_url_rule('/login/', 'login', views.login, methods=['GET', 'POST'])
auth.add_url_rule('/logout/', 'logout', views.logout)
auth.add_url_rule('/registration/', 'register', views.register, methods=['GET', 'POST'])
auth.add_url_rule('/registration/su', 'register_su',
                      views.register, defaults={'create_su': True}, methods=['GET', 'POST'])
auth.add_url_rule('/add-user/', 'add_user', views.add_user, methods=['GET', 'POST'])
auth.add_url_rule('/users/', view_func=views.Users.as_view('users'))
auth.add_url_rule('/users/edit/<username>', view_func=views.User.as_view('edit_user'))
auth.add_url_rule('/su-users/', view_func=views.SuUsers.as_view('su_users'))
auth.add_url_rule('/su-users/edit/<username>', view_func=views.SuUser.as_view('su_edit_user'))
auth.add_url_rule('/user/settings/', view_func=views.Profile.as_view('settings'))
auth.add_url_rule('/user/password/', view_func=views.Password.as_view('password'))
auth.errorhandler(403)(errors.handle_forbidden)




