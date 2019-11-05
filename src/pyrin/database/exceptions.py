# -*- coding: utf-8 -*-
"""
database exceptions module.
"""

from pyrin.core.exceptions import CoreException


class DatabaseManagerException(CoreException):
    """
    database manager exception.
    """
    pass


class InvalidSessionFactoryTypeError(DatabaseManagerException):
    """
    invalid session factory type error.
    """
    pass


class DuplicatedSessionFactoryError(DatabaseManagerException):
    """
    duplicated session factory error.
    """
    pass


class SessionFactoryNotExistedError(DatabaseManagerException):
    """
    session factory not existed error.
    """
    pass


class InvalidEntityTypeError(DatabaseManagerException):
    """
    invalid entity type error.
    """
    pass
