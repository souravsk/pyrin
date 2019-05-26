# -*- coding: utf-8 -*-
"""
deserializer number module.
"""

import re

from pyrin.converters.deserializer.handlers.base import StringPatternDeserializerBase
from pyrin.converters.deserializer.decorators import deserializer


@deserializer()
class IntegerDeserializer(StringPatternDeserializerBase):
    """
    integer deserializer class.
    """

    # matches the integer inside string.
    # example: 12, 232, 10, 0
    # all of these values will be matched.
    INTEGER_REGEX = re.compile(r'^([0-9])+$')

    def __init__(self, **options):
        """
        creates an instance of IntegerDeserializer.

        :keyword list[tuple(Pattern, int)] accepted_formats: a list of custom accepted formats
                                                             and their length for integer
                                                             deserialization.

        :type accepted_formats: list[tuple(Pattern format, int length)]
        """

        StringPatternDeserializerBase.__init__(self, **options)

    def deserialize(self, value, **options):
        """
        deserializes the given value.
        returns `DESERIALIZATION_FAILED` object if deserialization fails.

        :param str value: value to be deserialized.

        :rtype: int
        """

        deserializable, pattern = self.is_deserializable(value, **options)
        if not deserializable:
            return self.DESERIALIZATION_FAILED

        return int(value.strip())

    def get_default_formats(self):
        """
        gets default accepted formats that this
        deserializer could deserialize value from.

        :return: list(tuple(Pattern format, int length))

        :rtype: list(tuple(Pattern, int))
        """

        return [(self.INTEGER_REGEX, self.UNDEF_LENGTH)]


@deserializer()
class FloatDeserializer(StringPatternDeserializerBase):
    """
    float deserializer class.
    """

    # matches the float inside string.
    # example: 0.12, 2.32, 1.0, 0.0
    # all of these values will be matched.
    FLOAT_REGEX = re.compile(r'^([0-9])+[\.]([0-9])+$')

    def __init__(self, **options):
        """
        creates an instance of FloatDeserializer.

        :keyword list[tuple(Pattern, int)] accepted_formats: a list of custom accepted formats
                                                             and their length for float
                                                             deserialization.

        :type accepted_formats: list[tuple(Pattern format, int length)]
        """

        StringPatternDeserializerBase.__init__(self, **options)

    def deserialize(self, value, **options):
        """
        deserializes the given value.
        returns `DESERIALIZATION_FAILED` object if deserialization fails.

        :param str value: value to be deserialized.

        :rtype: float
        """

        deserializable, pattern = self.is_deserializable(value, **options)
        if not deserializable:
            return self.DESERIALIZATION_FAILED

        return float(value.strip())

    def get_default_formats(self):
        """
        gets default accepted formats that this
        deserializer could deserialize value from.

        :return: list(tuple(Pattern format, int length))

        :rtype: list(tuple(Pattern, int))
        """

        return [(self.FLOAT_REGEX, self.UNDEF_LENGTH)]