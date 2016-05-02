#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import current_app
from flask_principal import Permission, RoleNeed, UserNeed, identity_loaded
from flask_login import current_user

su_need = RoleNeed('su')

su_permission = Permission(su_need)
admin_permission = Permission(RoleNeed('admin')).union(su_permission)
editor_permission = Permission(RoleNeed('editor')).union(admin_permission)
writer_permission = Permission(RoleNeed('writer')).union(editor_permission)
reader_permission = Permission(RoleNeed('reader')).union(writer_permission)


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'username'):
        identity.provides.add(UserNeed(current_user.username))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'role'):
        # for role in current_user.roles:
        if current_user.is_superuser:
            identity.provides.add(su_need)

        identity.provides.add(RoleNeed(current_user.role))

