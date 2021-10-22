# -*- coding: utf-8 -*-
"""
admin users services module.
"""

from pyrin.application.services import get_component
from pyrin.admin.users import AdminUsersPackage


def create(username, password, confirm_password, first_name, last_name, **options):
    """
    creates a new admin user based on given inputs.

    :param str username: username.
    :param str password: password.
    :param str confirm_password: confirm password.
    :param str first_name: first name.
    :param str last_name: last name.

    :keyword str mobile: mobile number.
    :keyword str email: email address.
    :keyword int gender: gender.
    :enum gender:
        FEMALE = 0
        MALE = 1
        OTHER = 2

    :keyword bool is_active: is active user.
    :keyword bool is_superuser: is superuser.

    :raises PasswordsDoNotMatchError: passwords do not match error.
    """

    return get_component(AdminUsersPackage.COMPONENT_NAME).create(username, password,
                                                                  confirm_password,
                                                                  first_name, last_name,
                                                                  **options)


def update(id, **options):
    """
    updates the given admin user based on given inputs.

    :param int id: admin user id.

    :keyword str username: username.
    :keyword str password: password.
    :keyword str confirm_password: confirm password.
    :keyword str first_name: first name.
    :keyword str last_name: last name.
    :keyword str mobile: mobile number.
    :keyword str email: email address.
    :keyword int gender: gender.
    :enum gender:
        FEMALE = 0
        MALE = 1
        OTHER = 2

    :keyword bool is_active: is active user.
    :keyword bool is_superuser: is superuser.

    :raises PasswordsDoNotMatchError: passwords do not match error.
    """

    return get_component(AdminUsersPackage.COMPONENT_NAME).update(id, **options)
