# -*- coding: utf-8 -*-
"""
locale services module.
"""

from pyrin.application.services import get_component
from pyrin.globalization.locale import LocalePackage


def set_locale_selector(func):
    """
    sets the given function as locale selector.

    :param callable func: function to be set as locale selector.

    :raises InvalidLocaleSelectorTypeError: invalid locale selector type error.

    :raises LocaleSelectorHasBeenAlreadySetError: locale selector has been
                                                  already set error.
    """

    get_component(LocalePackage.COMPONENT_NAME).set_locale_selector(func)


def set_timezone_selector(func):
    """
    sets the given function as timezone selector.

    :param callable func: function to be set as timezone selector.

    :raises InvalidTimezoneSelectorTypeError: invalid timezone selector type error.

    :raises TimezoneSelectorHasBeenAlreadySetError: timezone selector has been
                                                    already set error.
    """

    get_component(LocalePackage.COMPONENT_NAME).set_timezone_selector(func)


def get_current_locale():
    """
    gets the current locale that should be used for current request.
    it never raises an error and returns the default locale if anything goes wrong.

    :rtype: str
    """

    return get_component(LocalePackage.COMPONENT_NAME).get_current_locale()


def get_current_timezone():
    """
    gets the current timezone that should be used for current request.
    it never raises an error and returns the default locale if anything goes wrong.

    :rtype: str
    """

    return get_component(LocalePackage.COMPONENT_NAME).get_current_timezone()