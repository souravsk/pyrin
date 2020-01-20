# -*- coding: utf-8 -*-
"""
utils sqlalchemy module.
"""

from sqlalchemy.orm import lazyload
from sqlalchemy import func

import pyrin.utils.datetime as datetime_utils

from pyrin.core.context import DTO
from pyrin.core.exceptions import CoreAssertionError
from pyrin.core.globals import _, LIST_TYPES


def entity_to_dict(entity, exposed_only=True):
    """
    converts the given entity into a dict and returns it.
    the result dict only contains the columns of the entity
    which their `hidden` attribute is set to False.

    :param CoreEntity entity: entity to be converted.

    :param bool exposed_only: if set to False, it returns all
                              columns of the entity as dict.
                              if not provided, defaults to True.
    
    :rtype: dict
    """

    if entity is None:
        return DTO()

    return entity.to_dict(exposed_only)


def dict_to_entity(entity_class, **kwargs):
    """
    converts the given keyword arguments into
    an specified entity and returns it.

    :param type entity_class: the result entity class type.

    :rtype: CoreEntity
    """

    result = entity_class()
    result.from_dict(**kwargs)
    return result


def entity_to_dict_list(entities, exposed_only=True):
    """
    converts the given list of entities into a
    list of dicts and returns the result.

    :param list[CoreEntity] entities: list of entities.

    :param bool exposed_only: if set to False, it returns all
                              columns of the entity as dict.
                              if not provided, defaults to True.

    :returns list[dict]
    :rtype list
    """

    results = []
    if entities is None or len(entities) <= 0:
        return results

    for single_entity in entities:
        results.append(single_entity.to_dict(exposed_only))

    return results


def tuple_to_dict(columns, values):
    """
    converts values tuple into a dict using given columns tuple.

    :param tuple[Column] columns: columns.
    :param tuple values: values to map to columns.

    :rtype: dict
    """

    if columns is None or values is None or len(columns) <= 0 or len(values) <= 0:
        return DTO()

    columns_length = len(columns)
    values_length = len(values)

    if columns_length != values_length:
        raise CoreAssertionError('length of columns which is [{column}] and '
                                 'values which is [{value}] does not match.'
                                 .format(column=columns_length,
                                         value=values_length))

    column_names = tuple(col.key for col in columns)
    return DTO(zip(column_names, values))


def tuple_to_dict_list(columns, values):
    """
    converts the given list of values tuple into a list
    of dicts using given columns tuple.

    :param tuple[Column] columns: columns.
    :param list[tuple] values: list of values.

    :returns list[dict]
    :rtype: list
    """

    results = []
    if columns is None or values is None or len(columns) <= 0 or len(values) <= 0:
        return results

    for single_value in values:
        results.append(tuple_to_dict(columns, single_value))

    return results


def like_both(value):
    """
    gets a copy of string with `%` attached to both
    ends of it to use in like operator.

    :param str value: value to be processed.

    :rtype: str
    """

    if value is None:
        value = ''

    return '%{value}%'.format(value=value)


def like_begin(value):
    """
    gets a copy of string with `%` attached to beginning
    of it to use in like operator.

    :param str value: value to be processed.

    :rtype: str
    """

    if value is None:
        value = ''

    return '%{value}'.format(value=value)


def like_end(value):
    """
    gets a copy of string with `%` attached to end
    of it to use in like operator.

    :param str value: value to be processed.

    :rtype: str
    """

    if value is None:
        value = ''

    return '{value}%'.format(value=value)


def count(query, column=None):
    """
    executes a count query using given query object and returns the result.

    this method generates a sql query like below:
    select count(column)
    from table
    where ...

    you should always use this method instead of sqlalchemy session.query.count()
    because session.query.count() is inefficient.

    :param Query query: sqlalchemy query object.

    :param Column column: column to perform count on it.
                          defaults to `*` if not provided.

    :rtype: int
    """

    func_count = func.count()
    if column is not None:
        func_count = func.count(column)

    statement = query.options(lazyload('*')).statement.with_only_columns(
        [func_count]).order_by(None)

    result = query.session.execute(statement).scalar()

    return result


def add_range_clause(clauses, column, value_lower, value_upper,
                     include_equal_to_lower=True,
                     include_equal_to_upper=True):
    """
    adds range comparison into given clauses using specified inputs.

    :param list clauses: clause list to add range clause to it.
    :param Column column: entity column to add range clause for it.
    :param object value_lower: lower bound of range clause.
    :param object value_upper: upper bound of range clause.

    :param include_equal_to_lower: specifies that lower value
                                   should be considered in range.
                                   defaults to True if not provided.

    :param include_equal_to_upper: specifies that upper value
                                   should be considered in range.
                                   defaults to True if not provided.
    """

    if value_lower is None and value_upper is None:
        return

    # we swap the upper and lower values in case of user mistake.
    if value_lower is not None and value_upper is not None and value_lower > value_upper:
        value_lower, value_upper = value_upper, value_lower

    if value_lower is not None and value_lower == value_upper:
        clauses.append(column == value_lower)
    else:
        if value_lower is not None:
            if include_equal_to_lower is True:
                clauses.append(column >= value_lower)
            else:
                clauses.append(column > value_lower)
        if value_upper is not None:
            if include_equal_to_upper is True:
                clauses.append(column <= value_upper)
            else:
                clauses.append(column < value_upper)


def add_date_range_clause(clauses, column, date_lower, date_upper,
                          include_equal_to_lower=True,
                          include_equal_to_upper=True,
                          **options):
    """
    adds date range comparison into given clauses using specified inputs.

    :param list clauses: clause list to add range clause to it.
    :param Column column: entity column to add range clause for it.
    :param datetime date_lower: lower bound of range clause.
    :param datetime date_upper: upper bound of range clause.

    :param include_equal_to_lower: specifies that lower date
                                   should be considered in range.
                                   defaults to True if not provided.

    :param include_equal_to_upper: specifies that upper date
                                   should be considered in range.
                                   defaults to True if not provided.

    :keyword bool consider_begin_of_day: specifies that consider begin
                                         of day for lower date.
                                         defaults to True if not provided.

    :keyword bool consider_end_of_day: specifies that consider end
                                       of day for upper date.
                                       defaults to True if not provided.
    """

    consider_begin_of_day = options.get('consider_begin_of_day', True)
    consider_end_of_day = options.get('consider_end_of_day', True)

    if date_lower is not None and consider_begin_of_day is True:
        date_lower = datetime_utils.begin_of_day(date_lower)

    if date_upper is not None and consider_end_of_day is True:
        date_upper = datetime_utils.end_of_day(date_upper)

    add_range_clause(clauses, column, date_lower, date_upper,
                     include_equal_to_lower, include_equal_to_upper)


def add_list_clause(clauses, column, value):
    """
    adds list or single comparison into clauses based on given value.

    :param list clauses: clause list to add comparison clause to it.
    :param Column column: entity column to add comparison clause for it.
    :param Union[object, list[object]] value: value to add comparison for it.
    """

    if value is not None:
        if isinstance(value, LIST_TYPES):
            clauses.append(column.in_(value))
        else:
            clauses.append(column == value)


def add_like_clause(clauses, column, value, string_wrapper=like_both):
    """
    adds like clause into clauses based on given inputs.

    :param list clauses: clause list to add like clause to it.
    :param Column column: entity column to add like clause for it.
    :param object value: value to add like clause for it.
    :param callable string_wrapper: a callable to provide a string
                                    to be used as value in like clause.
                                    defaults to `like_both` if not provided.
    """

    if value is not None:
        clauses.append(column.like(string_wrapper(value)))
