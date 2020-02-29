# -*- coding: utf-8 -*-
"""
database orm sql operators base module.
"""

from datetime import datetime

from sqlalchemy.sql.operators import ColumnOperators

import pyrin.utils.datetime as datetime_utils

from pyrin.utils.sqlalchemy import like_prefix, like_exact_prefix, \
    like_suffix, like_exact_suffix


class CoreColumnOperators(ColumnOperators):
    """
    core column operators class.
    this class provides some practical benefits
    to its subclasses for sql operations.
    """

    DEFAULT_ESCAPE_CHAR = '/'

    def between(self, cleft, cright, symmetric=False, **options):
        """
        produces an `expression.between` clause against the parent
        object, given the lower and upper range. this method is overridden
        to be able to handle datetime values more practical.

        :param object cleft: lower bound of clause.
        :param object cright: upper bound of clause.

        :param bool symmetric: specifies to emmit `between symmetric` to database.
                               note that not all databases support symmetric.
                               but `between symmetric` is equivalent to
                               `between least(a, b) and greatest(a, b)`.

        :keyword bool consider_begin_of_day: specifies that consider begin
                                             of day for lower datetime.
                                             defaults to True if not provided.
                                             this only has effect on datetime value.

        :keyword bool consider_end_of_day: specifies that consider end
                                           of day for upper datetime.
                                           defaults to True if not provided.
                                           this only has effect on datetime value.
        """

        consider_begin_of_day = options.get('consider_begin_of_day', True)
        consider_end_of_day = options.get('consider_end_of_day', True)
        is_lower_datetime = isinstance(cleft, datetime)
        is_upper_datetime = isinstance(cright, datetime)

        if consider_begin_of_day is True and is_lower_datetime is True:
            cleft = datetime_utils.begin_of_day(cleft)

        if consider_end_of_day is True and is_upper_datetime is True:
            cright = datetime_utils.end_of_day(cright)

        # swapping values in case of user mistake.
        if symmetric is True and is_lower_datetime is True \
                and is_upper_datetime is True and cleft > cright:
            cleft, cright = cright, cleft
            symmetric = False

        return super().between(cleft, cright, symmetric)

    def _process_like_autoescape(self, value, escape, autoescape):
        """
        processes the value based on autoescape flag for like command.
        it may return an escaped string or the exact input string.

        :param str value: value to be escaped.

        :param str escape: a character to be used as escape character.
                           defaults to `DEFAULT_ESCAPE_CHAR` if not provided.

        :keyword bool autoescape: establishes an escape character within the like
                                  expression, then applies it to all occurrences of
                                  `%`, `_` and the escape character itself within the
                                  comparison value.

        :rtype: str
        """

        if autoescape is True:
            if escape is None:
                escape = self.DEFAULT_ESCAPE_CHAR

            if escape not in ("%", "_"):
                value = value.replace(escape, escape + escape)

            value = value.replace("%", escape + "%").replace("_", escape + "_")

        return value

    def _process_like_prefix(self, value, **options):
        """
        processes the value that should be prefixed to

        value for `like` expression based on given options.

        :param str value: expression to be compared.

        :keyword bool exact_start: specifies that value should be emitted
                                   without any modifications at start of it.
                                   defaults to True if not provided.

        :keyword int start_count: count of `_` chars to be attached to beginning.
                                  if not provided, `%` will be used.

        :note start_count: this value has a limit of `LIKE_CHAR_COUNT_LIMIT`,
                           if the provided value goes upper than this limit,
                           a `%` will be attached instead of it. this limit
                           is for security reason.

        :rtype: str
        """

        exact_start = options.get('exact_start', True)
        if exact_start is False:
            begin_wrapper = like_prefix
            inputs = (value, )
            begin_count = options.get('start_count', None)
            if begin_count is not None:
                begin_wrapper = like_exact_prefix
                inputs = (value, begin_count)

            value = begin_wrapper(*inputs)

        return value

    def _process_like_suffix(self, value, **options):
        """
        processes the value that should be suffixed to
        value for `like` expression based on given options.

        :param str value: expression to be compared.

        :keyword bool exact_end: specifies that value should be emitted
                                 without any modifications at end of it.
                                 defaults to True if not provided.

        :keyword int end_count: count of `_` chars to be attached to end.
                                if not provided, `%` will be used.

        :note end_count: this value has a limit of `LIKE_CHAR_COUNT_LIMIT`,
                         if the provided value goes upper than this limit,
                         a `%` will be attached instead of it. this limit
                         is for security reason.

        :rtype: str
        """

        exact_end = options.get('exact_end', True)
        if exact_end is False:
            end_wrapper = like_suffix
            inputs = (value,)
            end_count = options.get('end_count', None)
            if end_count is not None:
                end_wrapper = like_exact_suffix
                inputs = (value, end_count)

            value = end_wrapper(*inputs)

        return value

    def istartswith(self, other, **options):
        """
        implements the `startswith` operator.
        produces an `ilike` expression that tests against a match for the
        start of a string value. for example:
        column like <other> || `%` or column like <other> || `_`
        this method provides a case-insensitive variant of `startswith()` method.

        :param str other: expression to be compared.

        :keyword str escape: optional escape character,
                             renders the `escape` keyword.

        :keyword bool autoescape: establishes an escape character within the like
                                  expression, then applies it to all occurrences of
                                  `%`, `_` and the escape character itself within the
                                  comparison value.

        :keyword int end_count: count of `_` chars to be attached to end.
                                if not provided, `%` will be used.

        :note end_count: this value has a limit of `LIKE_CHAR_COUNT_LIMIT`,
                         if the provided value goes upper than this limit,
                         a `%` will be attached instead of it. this limit
                         is for security reason.
        """

        escape = options.pop('escape', None)
        options.update(exact_end=False)
        other = self._process_like_autoescape(other, escape, options.get('autoescape', False))
        other = self._process_like_suffix(other, **options)
        return self.ilike(other, escape)

    def iendswith(self, other, **options):
        """
        implements the `endswith` operator.
        produces an `ilike` expression that tests against a match for the
        end of a string value. for example:
        column like '%' || <other> or column like '_' || <other>
        this method provides a case-insensitive variant of `endswith()` method.

        :param str other: expression to be compared.

        :keyword str escape: optional escape character,
                             renders the `escape` keyword.

        :keyword bool autoescape: establishes an escape character within the like
                                  expression, then applies it to all occurrences of
                                  `%`, `_` and the escape character itself within the
                                  comparison value.

        :keyword int start_count: count of `_` chars to be attached to start.
                                  if not provided, `%` will be used.

        :note start_count: this value has a limit of `LIKE_CHAR_COUNT_LIMIT`,
                           if the provided value goes upper than this limit,
                           a `%` will be attached instead of it. this limit
                           is for security reason.
        """

        escape = options.pop('escape', None)
        options.update(exact_start=False)
        other = self._process_like_autoescape(other, escape, options.get('autoescape', False))
        other = self._process_like_prefix(other, **options)
        return self.ilike(other, escape)

    def icontains(self, other, **options):
        """
        implements the 'contains' operator.
        produces an `ilike` expression that tests against a match for the
        middle of a string value. for example:
        column like `%` || <other> || `%` or column like `_` || <other> || `_`
        this method provides a case-insensitive variant of `contains()` method.

        :param str other: expression to be compared.

        :keyword str escape: optional escape character,
                             renders the `escape` keyword.

        :keyword bool autoescape: establishes an escape character within the like
                                  expression, then applies it to all occurrences of
                                  `%`, `_` and the escape character itself within the
                                  comparison value.

        :keyword int start_count: count of `_` chars to be attached to beginning.
                                  if not provided, `%` will be used.

        :keyword int end_count: count of `_` chars to be attached to end.
                                if not provided, `%` will be used.

        :note start_count, end_count: this value has a limit of `LIKE_CHAR_COUNT_LIMIT`,
                                      if the provided value goes upper than this limit,
                                      a `%` will be attached instead of it. this limit
                                      is for security reason.
        """

        escape = options.pop('escape', None)
        options.update(exact_start=False, exact_end=False)
        other = self._process_like_autoescape(other, escape, options.get('autoescape', False))
        other = self._process_like_prefix(other, **options)
        other = self._process_like_suffix(other, **options)
        return self.ilike(other, escape)