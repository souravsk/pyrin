# -*- coding: utf-8 -*-
"""
logging adapters module.
"""

from logging import LoggerAdapter

import pyrin.security.session.services as session_services
import pyrin.logging.services as logging_services


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

        super().__init__(logger, dict())

        # these attributes have been added for compatibility
        # with loggers common api.
        self.handlers = logger.handlers
        self.level = logger.level
        self.propagate = logger.propagate
        self.parent = logger.parent

    def addHandler(self, hdlr):
        """
        adds the specified handler to this logger.

        this method has been added for compatibility
        with loggers common api.

        :param Handler hdlr: logger handler to be added.
        """

        self.logger.addHandler(hdlr)

    def removeHandler(self, hdlr):
        """
        removes the specified handler from this logger.

        this method has been added for compatibility
        with loggers common api.

        :param Handler hdlr: logger handler to be removed.
        """

        self.logger.removeHandler(hdlr)

    def process(self, msg, kwargs):
        """
        processes the logging message and keyword arguments passed in to a logging call.

        it's to insert contextual information. you can either manipulate
        the message itself, the keyword args or both. return the message
        and kwargs modified (or not) to suit your needs.

        :param str msg: log message.
        :param dict kwargs: keyword arguments passed to logging call.

        :keyword dict data: data to be used for interpolation.

        :returns: tuple[str message, dict kwargs]
        :rtype: tuple[str, dict]
        """

        data = kwargs.pop('data', None)
        if data is not None:
            msg = logging_services.interpolate(msg, data)

        custom_message, custom_kwargs = self._process(msg, kwargs)
        return super().process(custom_message, custom_kwargs)

    def _process(self, msg, kwargs):
        """
        processes the logging message and keyword arguments passed in to a logging call.

        it's to insert contextual information. you can either manipulate
        the message itself, the keyword args or both. return the message
        and kwargs modified (or not) to suit your needs.

        this method is intended to be overridden in subclasses.

        :param str msg: log message.
        :param dict kwargs: keyword arguments passed to logging call.

        :returns: tuple[str message, dict kwargs]
        :rtype: tuple[str, dict]
        """

        return msg, kwargs


class RequestInfoLoggerAdapter(BaseLoggerAdapter):
    """
    request info logger adapter.

    this adapter adds request info into generated logs.
    """

    def _process(self, msg, kwargs):
        """
        processes the logging message and keyword arguments passed in to a logging call.

        it's to insert contextual information. you can either manipulate
        the message itself, the keyword args or both. return the message
        and kwargs modified (or not) to suit your needs.

        :param str msg: log message.
        :param dict kwargs: keyword arguments passed to logging call.

        :returns: tuple[str message, dict kwargs]
        :rtype: tuple[str, dict]
        """

        client_request = session_services.get_safe_current_request()
        request_info = ''
        if client_request is not None:
            request_info = '[{client_request}]: '.format(client_request=client_request)

        custom_message = '{request_info}{message}'.format(request_info=request_info,
                                                          message=msg)
        return custom_message, kwargs
