#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from flask import render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required

from . import models, forms


def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.objects.get(username=form.username.data)
        except models.User.DoesNotExist:
            user = None

        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))

        flash('Invalid username or password', 'danger')

    return render_template('accounts/login.html', form=form)


def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = models.User()
        user.username = form.username.data
        user.password = form.password.data
        user.email = form.email.data
        user.save()

        return redirect(url_for('main.index'))

    return render_template('accounts/registration.html', form=form)


@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'logout')
    return redirect(url_for('main.index'))
