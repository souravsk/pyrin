# -*- coding: utf-8 -*-
"""
hashing handlers base module.
"""

from pyrin.core.context import CoreObject
from pyrin.core.exceptions import CoreNotImplementedError


class HashingBase(CoreObject):
    """
    hashing base class.
    all application hashing handlers must be subclassed from this.
    """

    def __init__(self, name, **options):
        """
        initializes an instance of HashingBase.

        :param str name: name of the hashing handler.
        """

        CoreObject.__init__(self)

        self._set_name(name)

    def generate_hash(self, plain_text, salt):
        """
        gets the hash of input plain text and salt.

        :param str plain_text: text to be hashed.
        :param str salt: salt to append to plain text before hashing.

        :raises CoreNotImplementedError: core not implemented error.

        :rtype: str
        """

        raise CoreNotImplementedError()

    def generate_salt(self, **options):
        """
        generates a valid salt for this handler and returns it.

        :keyword int length: length of generated salt.
                             some hashing handlers may not accept custom salt length,
                             so this value would be ignored on those handlers.

        :raises CoreNotImplementedError: core not implemented error.

        :rtype: str
        """

        raise CoreNotImplementedError()

    def is_valid(self, plain_text, hashed_value):
        """
        gets a value indicating that given plain text's
        hash is identical to given hashed value.

        :param str plain_text: text to be hashed.
        :param str hashed_value: hashed value to compare with.

        :raises CoreNotImplementedError: core not implemented error.

        :rtype: bool
        """

        raise CoreNotImplementedError()

    def _get_algorithm(self):
        """
        gets the hashing algorithm.

        :raises CoreNotImplementedError: core not implemented error.

        :rtype: str
        """

        raise CoreNotImplementedError()
