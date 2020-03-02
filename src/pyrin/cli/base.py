# -*- coding: utf-8 -*-
"""
cli base module.
"""

import subprocess

from subprocess import CalledProcessError
from threading import Lock

from pyrin.cli.metadata import ArgumentMetadataBase, PositionalArgumentMetadata
from pyrin.core.context import CoreObject
from pyrin.core.exceptions import CoreNotImplementedError
from pyrin.core.globals import LIST_TYPES
from pyrin.utils.singleton import MultiSingletonMeta
from pyrin.cli.exceptions import InvalidCLIHandlerNameError, InvalidArgumentMetaDataTypeError, \
    PositionalArgumentsIndicesError


class CLIHandlerSingletonMeta(MultiSingletonMeta):
    """
    cli handler singleton meta class.
    this is a thread-safe implementation of singleton.
    """

    _instances = dict()
    _lock = Lock()


class AbstractCLIHandlerBase(CoreObject, metaclass=CLIHandlerSingletonMeta):
    """
    abstract cli handler base class.
    """

    def get_name(self):
        """
        gets current handler name, the handler will be registered with this name.

        the name must be the exact command name that this handler handles.
        for example `revision`.

        :raises CoreNotImplementedError: core not implemented error.

        :rtype: str
        """

        raise CoreNotImplementedError()

    def execute(self, **options):
        """
        executes the current cli command with given inputs.

        :raises CoreNotImplementedError: core not implemented error.

        :returns: execution result.
        """

        raise CoreNotImplementedError()

    def _process_arguments(self):
        """
        processes the arguments that are related to this handler.

        this method is intended to be overridden by each concrete handler.
        every class that overrides this, must call `super()._process_arguments()`
        after its work has been done.
        """
        pass


class CLIHandlerBase(AbstractCLIHandlerBase):
    """
    cli handler base class.
    all application cli handlers must be subclassed from this.
    """

    def __init__(self, name, **options):
        """
        initializes an instance of CLIHandlerBase.

        :param str name: the handler name that should be registered
                         with. this name must be the exact name that
                         this handler must emmit to cli.

        :raises InvalidCLIHandlerNameError: invalid cli handler name error.
        :raises PositionalArgumentsIndicesError: positional arguments indices error.
        """

        super().__init__()

        if name in (None, '') or name.isspace():
            raise InvalidCLIHandlerNameError('CLI handler name must be provided.')

        self._name = name
        self._arguments_metadata = []
        self.process_arguments()

    def __str__(self):
        """
        gets the string representation of current cli handler.

        :rtype: str
        """

        return '{base} [{handler}]'.format(base=super().__str__(), handler=self._name)

    def get_name(self):
        """
        gets current handler name, the handler will be registered with this name.

        the name must be the exact command name that this handler handles.
        for example `revision`.

        :rtype: str
        """

        return self._name

    def process_arguments(self):
        """
        processes the arguments that are related to this handler.

        :raises PositionalArgumentsIndicesError: positional arguments indices error.
        """

        self._process_arguments()
        self._validate_positional_arguments()

    def _validate_positional_arguments(self):
        """
        validates the positional arguments of this handler.

        it will make sure that their indices are correct.

        :raises PositionalArgumentsIndicesError: positional arguments indices error.
        """

        positionals = [item for item in self._arguments_metadata
                       if isinstance(item, PositionalArgumentMetadata)]

        length = len(positionals)
        if length > 0:
            indices = sorted([item.index for item in positionals])
            required_indices = sorted([item for item in range(length)])

            if indices != required_indices:
                raise PositionalArgumentsIndicesError('CLI handler [{handler}] has '
                                                      '{length} positional arguments {args}, '
                                                      'but indices of positional arguments are '
                                                      'incorrect. indices must be in the '
                                                      'range of {indices} for each argument '
                                                      'and it must be unique per argument. '
                                                      'the current indices are {current}.'
                                                      .format(handler=self,
                                                              length=length,
                                                              args=positionals,
                                                              indices=required_indices,
                                                              current=indices))

    def _add_argument_metadata(self, item):
        """
        adds the given item into this handlers argument metadata.

        :param ArgumentMetadataBase item: argument metadata to be added.

        :raises InvalidArgumentMetaDataTypeError: invalid argument metadata type error.
        """

        if not isinstance(item, ArgumentMetadataBase):
            raise InvalidArgumentMetaDataTypeError('Input parameter [{param}] is not '
                                                   'an instance of [{instance}].'
                                                   .format(param=item,
                                                           instance=ArgumentMetadataBase))

        self._arguments_metadata.append(item)

    def execute(self, **options):
        """
        executes the current cli command with given inputs.

        :rtype: int
        """

        return self._execute(**options)

    def _execute(self, **options):
        """
        executes the current cli command with given inputs.

        :rtype: int
        """

        processed_inputs = self._process_inputs(**options)
        bounded_options = self._bind_cli_arguments(**processed_inputs)
        common_options = self._get_common_cli_options()
        common_options.extend(bounded_options)
        return self._execute_on_cli(common_options)

    def _execute_on_cli(self, commands):
        """
        executes the current cli command with given inputs.

        :param list commands: a list of all commands and their
                              values to be sent to cli command.

        :rtype: int
        """

        try:
            result = subprocess.check_call(commands)
            return self._process_return_value(result)
        except CalledProcessError as error:
            return self._process_return_value(error.returncode)

    def _process_return_value(self, result):
        """
        processes the return value from cli command execution.

        this method returns the None value and is intended to be overridden
        by subclasses if required. if a cli handlers group does need to return
        a value, it could override this method and return the desired value.

        :param int result: result value returned from cli command.

        :rtype: None
        """

        return None

    def _process_inputs(self, **options):
        """
        processes the inputs given to this handler and returns them.

        subclasses could override this method and modify inputs as needed.
        if the modification is a static one, you could provide default in
        the `ArgumentMetadata` of the relevant `CLIParamMixin`, but if the
        modification is not static, for example, a callable must be used
        to generate value based on current situation, you must use this method
        to modify inputs and inject the correct value. subclasses must call
        `super()._process_inputs(**options)` after they're done.

        :rtype: dict
        """

        return options

    def _get_common_cli_options(self):
        """
        gets the list of common cli options.

        this method is intended to be overridden by subclasses
        to inject some common cli options into the commands list.
        subclasses must return a list containing all common options.
        the common options will be inserted into beginning of the commands list.

        :rtype: list
        """

        return []

    def _bind_cli_arguments(self, **options):
        """
        binds cli arguments of current handler with values available in options.

        options are a mapping of real python method inputs.

        :returns: list of all commands in the form of:
                  [str name1, str value1, ...] or
                  [str name1, str value1, str value2, ...]

        :rtype: list
        """

        commands = [self.get_name()]
        for metadata in self._arguments_metadata:
            real_value = options.get(metadata.param_name, None)
            representation = metadata.get_representation(real_value)

            if representation is None:
                continue

            if isinstance(metadata, PositionalArgumentMetadata):
                if isinstance(representation, LIST_TYPES):
                    self._inject_positional_arguments(commands, representation,
                                                      metadata.index + 1)
                else:
                    commands.insert(metadata.index + 1, representation)
            elif isinstance(representation, LIST_TYPES):
                commands.extend(representation)
            else:
                commands.append(representation)

        return commands

    def _inject_positional_arguments(self, commands, arguments, index):
        """
        injects(in-place) given arguments into specified index of given commands list.

        :param list[object] commands: list of cli commands.

        :param list[object] arguments: arguments that must be
                                       injected into commands list.

        :param index: zero-based index in which arguments must be injected.
        """

        for i in range(len(arguments)):
            commands.insert(index + i, arguments[i])
