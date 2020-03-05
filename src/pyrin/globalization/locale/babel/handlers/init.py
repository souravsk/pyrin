# -*- coding: utf-8 -*-
"""
babel handlers init module.
"""

from pyrin.globalization.locale.babel.interface import BabelCLIHandlerBase
from pyrin.globalization.locale.babel.decorators import babel_cli_handler
from pyrin.globalization.locale.babel.handlers.params import DomainParam, \
    InputTemplateFileParam, OutputDirectoryParam, LocaleParam, WidthParam, NoWrapParam


@babel_cli_handler()
class InitCLIHandler(BabelCLIHandlerBase):
    """
    init cli handler class.
    """

    def __init__(self):
        """
        initializes an instance of InitCLIHandler.
        """

        super().__init__('init')

    def _inject_params(self, params):
        """
        injects all the params of current handler into given list.

        :param list[CLIParamBase] params: list of all params.
        """

        params.extend([DomainParam(), InputTemplateFileParam(),
                       OutputDirectoryParam(), LocaleParam(),
                       WidthParam(), NoWrapParam()])

        return super()._inject_params(params)
