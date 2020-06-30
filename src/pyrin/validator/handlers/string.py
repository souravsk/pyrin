# -*- coding: utf-8 -*-
"""
validator handlers string module.
"""

import re

from pyrin.core.globals import _
from pyrin.validator.handlers.base import ValidatorBase
from pyrin.validator.handlers.exceptions import InvalidStringLengthError, \
    ValueCouldNotBeBlankError, ValueCouldNotBeWhitespaceError, ValueDoesNotMatchPatternError, \
    InvalidRegularExpressionError, RegularExpressionMustBeProvidedError, ValueIsNotStringError, \
    MinimumLengthHigherThanMaximumLengthError


class StringValidator(ValidatorBase):
    """
    string validator class.
    """

    invalid_type_error = ValueIsNotStringError
    invalid_type_message = _('The provided value for [{param_name}] '
                             'must be a string.')
    invalid_length_error = InvalidStringLengthError
    invalid_length_message = _('The provided value for [{param_name}] '
                               'has an invalid length.')
    blank_value_error = ValueCouldNotBeBlankError
    blank_value_message = _('The provided value for [{param_name}] '
                            'could not be blank.')
    whitespace_value_error = ValueCouldNotBeWhitespaceError
    whitespace_value_message = _('The provided value for [{param_name}] '
                                 'could not be whitespace.')

    def __init__(self, domain, name, **options):
        """
        initializes an instance of StringValidator.

        :param type[BaseEntity] | str domain: the domain in which this validator
                                              must be registered. it could be a
                                              type of a BaseEntity subclass.
                                              if a validator must be registered
                                              independent from any BaseEntity subclass,
                                              the domain could be a unique string name.
                                              note that the provided string name must be
                                              unique at application level.

        :param str name: validator name.
                         each validator will be registered with its name
                         in corresponding domain.
                         to enable automatic validations, the provided
                         name must be the exact name of the parameter
                         which this validator will validate.

        :keyword bool nullable: specifies that null values should be accepted as valid.
                                defaults to True if not provided.

        :keyword str localized_name: localized name of the parameter
                                     which this validator will validate.
                                     it must be passed using `_` method
                                     from `pyrin.core.globals`.
                                     defaults to `name` if not provided.

        :keyword bool allow_blank: specifies that empty strings should be accepted
                                   as valid. defaults to True if not provided.

        :keyword bool allow_whitespace: specifies that whitespace strings should be accepted
                                        as valid. defaults to False if not provided.

        :keyword int minimum_length: specifies the minimum valid length for string value.
                                     no min length checking will be done if not provided.

        :keyword int maximum_length: specifies the maximum valid length for string value.
                                     no max length checking will be done if not provided.

        :raises ValidatorNameIsRequiredError: validator name is required error.
        :raises InvalidValidatorDomainError: invalid validator domain error.
        :raises InvalidValidationExceptionTypeError: invalid validation exception type error.
        :raises InvalidStringLengthError: invalid string length error.
        :raises ValueCouldNotBeBlankError: value could not be blank error.
        :raises ValueCouldNotBeWhitespaceError: value could not be whitespace error.
        :raises MinimumLengthHigherThanMaximumLengthError: minimum length higher than
                                                           maximum length error.
        """

        options.update(accepted_type=str)
        super().__init__(domain, name, **options)

        allow_blank = options.get('allow_blank', None)
        if allow_blank is None:
            allow_blank = True

        allow_whitespace = options.get('allow_whitespace', None)
        if allow_whitespace is None:
            allow_whitespace = False

        self._minimum_length = options.get('minimum_length', None)
        self._maximum_length = options.get('maximum_length', None)
        if self._minimum_length is not None and self._maximum_length is not None \
                and self._minimum_length > self._maximum_length:
            raise MinimumLengthHigherThanMaximumLengthError('Minimum length of string '
                                                            'could not be higher than '
                                                            'maximum length.')

        self._allow_blank = allow_blank
        self._allow_whitespace = allow_whitespace

        self._validate_exception_type(self.invalid_length_error)
        self._validate_exception_type(self.blank_value_error)
        self._validate_exception_type(self.whitespace_value_error)

    def _validate(self, value, **options):
        """
        validates the given value.

        it raises an error if validation fails.
        the raised error must be an instance of ValidationError.
        each overridden method must call `super()._validate()`
        preferably at the beginning.

        :param str value: value to be validated.

        :keyword bool allow_blank: determines that empty strings should be
                                   considered valid. this value has precedence
                                   over `allow_blank` instance attribute
                                   if provided.

        :keyword bool allow_whitespace: determines that whitespace strings should be
                                        considered valid. this value has precedence
                                        over `allow_whitespace` instance attribute
                                        if provided.

        :raises InvalidStringLengthError: invalid string length error.
        :raises ValueCouldNotBeBlankError: value could not be blank error.
        :raises ValueCouldNotBeWhitespaceError: value could not be whitespace error.
        """

        super()._validate(value, **options)

        allow_blank = options.get('allow_blank', None) or self.allow_blank
        allow_whitespace = options.get('allow_whitespace', None) or self.allow_whitespace
        length = len(value)
        if self.maximum_length is not None and length > self.maximum_length:
            raise self.invalid_length_error(self.invalid_length_message.format(
                param_name=self.localized_name))

        if self.minimum_length is not None and length < self.minimum_length:
            raise self.invalid_length_error(self.invalid_length_message.format(
                param_name=self.localized_name))

        if allow_blank is not True and length == 0:
            raise self.blank_value_error(self.blank_value_message.format(
                param_name=self.localized_name))

        if allow_whitespace is not True and value.isspace():
            raise self.whitespace_value_error(self.whitespace_value_message.format(
                param_name=self.localized_name))

        if length > 0 and not value.isspace():
            self._validate_extra(value, **options)

    def _validate_extra(self, value, **options):
        """
        validates the given value.

        this method is intended to be overridden by subclasses.
        it raises an error if validation fails.
        the raised error must be an instance of ValidationError.
        each overridden method must call `super()._validate_extra()`
        preferably at the beginning.

        :param str value: value to be validated.

        :raises ValidationError: validation error.
        """
        pass

    @property
    def minimum_length(self):
        """
        gets the minimum accepted length of this validator.

        returns None if no minimum has been set.

        :rtype: int
        """

        return self._minimum_length

    @property
    def maximum_length(self):
        """
        gets the maximum accepted length of this validator.

        returns None if no maximum has been set.

        :rtype: int
        """

        return self._maximum_length

    @property
    def allow_blank(self):
        """
        gets a value indicating that empty strings are considered valid.

        :rtype: bool
        """

        return self._allow_blank

    @property
    def allow_whitespace(self):
        """
        gets a value indicating that whitespace strings are considered valid.

        :rtype: bool
        """

        return self._allow_whitespace


class RegexValidator(StringValidator):
    """
    regex validator class.
    """

    # the regular expression to use for validation.
    # it could be set with a string containing a regex
    # or with a `Pattern` object from re.compile() method.
    regex = None
    pattern_not_match_error = ValueDoesNotMatchPatternError
    pattern_not_match_message = _('The provided value for [{param_name}] '
                                  'does not match the required pattern.')

    def __init__(self, domain, name, **options):
        """
        initializes an instance of RegexValidator.

        :param type[BaseEntity] | str domain: the domain in which this validator
                                              must be registered. it could be a
                                              type of a BaseEntity subclass.
                                              if a validator must be registered
                                              independent from any BaseEntity subclass,
                                              the domain could be a unique string name.
                                              note that the provided string name must be
                                              unique at application level.

        :param str name: validator name.
                         each validator will be registered with its name
                         in corresponding domain.
                         to enable automatic validations, the provided
                         name must be the exact name of the parameter
                         which this validator will validate.

        :keyword bool nullable: specifies that null values should be accepted as valid.
                                defaults to True if not provided.

        :keyword str localized_name: localized name of the parameter
                                     which this validator will validate.
                                     it must be passed using `_` method
                                     from `pyrin.core.globals`.
                                     defaults to `name` if not provided.

        :keyword bool allow_blank: specifies that empty strings should be accepted
                                   as valid. defaults to True if not provided.

        :keyword bool allow_whitespace: specifies that whitespace strings should be accepted
                                        as valid. defaults to False if not provided.

        :keyword int minimum_length: specifies the minimum valid length for string value.
                                     no min length checking will be done if not provided.

        :keyword int maximum_length: specifies the maximum valid length for string value.
                                     no max length checking will be done if not provided.

        :keyword int flags: flags to be used for regular expression
                            compilation using `re.compile` method.
                            this will only be used if a string regex is provided.

        :raises ValidatorNameIsRequiredError: validator name is required error.
        :raises InvalidValidatorDomainError: invalid validator domain error.
        :raises InvalidValidationExceptionTypeError: invalid validation exception type error.
        :raises InvalidStringLengthError: invalid string length error.
        :raises ValueCouldNotBeBlankError: value could not be blank error.
        :raises ValueCouldNotBeWhitespaceError: value could not be whitespace error.
        :raises InvalidRegularExpressionError: invalid regular expression error.
        :raises RegularExpressionMustBeProvidedError: regular expression must be provided error.
        """

        super().__init__(domain, name, **options)

        is_string = isinstance(self.regex, str)
        if not isinstance(self.regex, re.Pattern) and not is_string:
            raise InvalidRegularExpressionError('The provided regular expression is invalid. '
                                                'it must be a string containing a regular '
                                                'expression or a Pattern object returned from '
                                                're.compile() method.')

        if is_string and (len(self.regex) <= 0 or self.regex.isspace()):
            raise RegularExpressionMustBeProvidedError('The provided string for regular '
                                                       'expression could not be blank.')

        if is_string:
            flags = options.get('flags', None)
            if flags is None:
                flags = 0
            self._pattern = re.compile(self.regex, flags=flags)
        else:
            self._pattern = self.regex

        self._validate_exception_type(self.pattern_not_match_error)

    def _validate_extra(self, value, **options):
        """
        validates the given value.

        this method is intended to be overridden by subclasses.
        it raises an error if validation fails.
        the raised error must be an instance of ValidationError.
        each overridden method must call `super()._validate_extra()`
        preferably at the beginning.

        :param str value: value to be validated.

        :raises InvalidStringLengthError: invalid string length error.
        :raises ValueCouldNotBeBlankError: value could not be blank error.
        :raises ValueCouldNotBeWhitespaceError: value could not be whitespace error.
        :raises ValueDoesNotMatchPatternError: value does not match pattern error.
        """

        super()._validate_extra(value, **options)

        if not self.regex.match(value):
            raise self.pattern_not_match_error(
                self.pattern_not_match_message.format(param_name=self.localized_name))

    @property
    def pattern(self):
        """
        gets the pattern of this validator.

        :rtype: re.Pattern
        """

        return self._pattern