# -*- coding: utf-8 -*-
"""
deserializer boolean module.
"""

import re

from pyrin.converters.deserializer.handlers.base import StringPatternDeserializerBase
from pyrin.converters.deserializer.decorators import deserializer


@deserializer()
class NoneDeserializer(StringPatternDeserializerBase):
    """
    none deserializer class.
    """

    # matches the none inside string.
    # example: none, null
    # matching are case-insensitive.
    NONE_REGEX = re.compile(r'^none$', re.IGNORECASE)
    NULL_REGEX = re.compile(r'^null$', re.IGNORECASE)

    def __init__(self, **options):
        """
        creates an instance of NoneDeserializer.

        :keyword list[tuple(Pattern, int)] accepted_formats: a list of custom accepted formats
                                                             and their length for none
                                                             deserialization.

        :type accepted_formats: list[tuple(Pattern format, int length)]
        """

        StringPatternDeserializerBase.__init__(self, **options)

    def deserialize(self, value, **options):
        """
        deserializes the given value.
        returns `DESERIALIZATION_FAILED` object if deserialization fails.

        :param str value: value to be deserialized.

        :rtype: none
        """

        deserializable, pattern = self.is_deserializable(value, **options)
        if not deserializable:
            return self.DESERIALIZATION_FAILED

        return None

    def get_default_formats(self):
        """
        gets default accepted formats that this
        deserializer could deserialize value from.

        :return: list(tuple(Pattern format, int length))

        :rtype: list(tuple(Pattern, int))
        """

        return [(self.NONE_REGEX, 4),
                (self.NULL_REGEX, 4)]