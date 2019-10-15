# -*- coding: utf-8 -*-
"""
sequence package.
"""

from pyrin.packaging.context import Package


class SequencePackage(Package):
    """
    sequence package class.
    """

    NAME = __name__
    DEPENDS = []
    COMPONENT_NAME = 'database.sequence.component'