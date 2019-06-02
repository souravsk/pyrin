# -*- coding: utf-8 -*-
"""
logging services module.
"""

from pyrin.application.services import get_component
from pyrin.logging import LoggingPackage


def reload_configs(**options):
    """
    reloads all logging configurations from config file.
    """

    return get_component(LoggingPackage.COMPONENT_NAME).reload_configs(**options)


def get_logger(name, **options):
    """
    gets the logger based on input parameters.

    :param str name: logger name to get.

    :returns: specified logger.

    :rtype: Logger
    """

    return get_component(LoggingPackage.COMPONENT_NAME).get_logger(name, **options)


def debug(msg, *args, **kwargs):
    """
    emits a log with debug level.

    :param str msg: log message.
    """

    return get_component(LoggingPackage.COMPONENT_NAME).debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """
    emits a log with info level.

    :param str msg: log message.
    """

    return get_component(LoggingPackage.COMPONENT_NAME).info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    """
    emits a log with warning level.

    :param str msg: log message.
    """

    return get_component(LoggingPackage.COMPONENT_NAME).warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    """
    emits a log with error level.

    :param str msg: log message.
    """

    return get_component(LoggingPackage.COMPONENT_NAME).error(msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    """
    emits a log with error level and exception information.

    :param str msg: log message.
    """

    return get_component(LoggingPackage.COMPONENT_NAME).exception(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    """
    emits a log with critical level.

    :param str msg: log message.
    """

    return get_component(LoggingPackage.COMPONENT_NAME).critical(msg, *args, **kwargs)