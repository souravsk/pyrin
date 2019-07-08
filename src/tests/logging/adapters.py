# -*- coding: utf-8 -*-
"""
logging adapters module.
"""

from logging import LoggerAdapter

import pyrin.security.session.services as session_services

from pyrin.core.exceptions import CoreNotImplementedError


class BaseLoggerAdapter(LoggerAdapter):
    """
    base logger adapter class.
    all logger adapters should be subclassed from this.
    """

    def __init__(self, logger):
        """
        initializes an instance of BaseLoggerAdapter.

        :param Logger logger: logger instance to be wrapped.
        """

        LoggerAdapter.__init__(self, logger, {})

        # these attributes has been added for compatibility
        # with loggers common api.
        self.handlers = logger.handlers
        self.level = logger.level
        self.propagate = logger.propagate
        self.parent = logger.parent

    def process(self, msg, kwargs):
        """
        processes the logging message and keyword arguments passed in to
        a logging call to insert contextual information. you can either
        manipulate the message itself, the keyword args or both. return
        the message and kwargs modified (or not) to suit your needs.

        normally, you'll only need to override this one method in a
        `LoggerAdapter` subclass for your specific needs.

        :raises CoreNotImplementedError: core not implemented error.

        :returns: tuple(str message, dict kwargs)

        :rtype: tuple
        """

        raise CoreNotImplementedError()


class RequestInfoLoggerAdapter(BaseLoggerAdapter):
    """
    request info logger adapter.
    this adapter adds request info into generated logs.
    """

    def process(self, msg, kwargs):
        """
        processes the logging message and keyword arguments passed in to
        a logging call to insert contextual information. you can either
        manipulate the message itself, the keyword args or both. return
        the message and kwargs modified (or not) to suit your needs.

        :returns: tuple(str message, dict kwargs)

        :rtype: tuple
        """

        client_request = session_services.get_safe_current_request()
        custom_message = '[{client_request}]: {message}'.format(client_request=client_request,
                                                                message=msg)
        return custom_message, kwargs
