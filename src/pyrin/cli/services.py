# -*- coding: utf-8 -*-
"""
cli services module.
"""

from pyrin.application.services import get_component
from pyrin.cli import CLIPackage


def process_function(func, func_args, func_kwargs):
    """
    processes the given cli handler function with given inputs.

    :param function func: function to update its original inputs.
    :param tuple func_args: a tuple of function positional inputs.
    :param dict func_kwargs: a dictionary of function keyword arguments.

    :raises CLIHandlerNotFoundError: cli handler not found error.
    :raises InvalidCLIDecoratedMethodError: invalid cli decorated method error.

    :rtype: int
    """

    return get_component(CLIPackage.COMPONENT_NAME).process_function(func, func_args,
                                                                     func_kwargs)
