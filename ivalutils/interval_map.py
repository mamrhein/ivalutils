# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Name:        interval_map
# Purpose:     Mappings on intervals
#
# Author:      Michael Amrhein (michael@adrhinum.de)
#
# Copyright:   (c) 2016 ff. Michael Amrhein
# License:     This program is part of a larger application. For license
#              details please read the file LICENSE.TXT provided together
#              with the application.
# ----------------------------------------------------------------------------
# $Source$
# $Revision$


"""Mappings on intervals

Usage
=====

Creating interval mappings
--------------------------

The class :class:`IntervalMapping` is used to create a mapping from intervals
to arbitrary values.

Instances can be created by giving an IntervalChain and a sequence of
associated values ...:

    >>> im1 = IntervalMapping(IntervalChain((0, 300, 500, 1000)), \
(0., .10, .15, .20))

... or a sequence of limiting values and a sequence of associated values ...:

    >>> im2 = IntervalMapping((0, 300, 500, 1000), (0., .10, .15, .20))

... or a sequence of tuples, each holding a limiting value and an associated
value:

    >>> im3 = IntervalMapping(((0, 0.), (300, .10), (500, .15), (1000, .20)))
    >>> im1 == im2 == im3
    True

Operations on IntervalMappings
------------------------------

Interval mappings behave like ordinary mappings:

    >>> list(im3.keys())
    [Interval(lower_limit=Limit(True, 0, True), upper_limit=Limit(False, \
300, False)),
     Interval(lower_limit=Limit(True, 300, True), upper_limit=Limit(False, \
500, False)),
     Interval(lower_limit=Limit(True, 500, True), upper_limit=Limit(False, \
1000, False)),
     Interval(lower_limit=Limit(True, 1000, True))]
    >>> list(im3.values())
    [0.0, 0.1, 0.15, 0.2]
    >>> im3[Interval(lower_limit=Limit(True, 300, True), upper_limit=\
Limit(False, 500, False))]
    0.1

In addition they can be looked-up for the value associated with the interval
which contains a given value:

    >>> im3.map(583)
    0.15

As a short-cut, the interval mapping can be used like a function:

    >>> im3(412)
    0.1

Use cases for interval mappings are for example:

  * determine the discount to be applied depending on an order value,
  * rating customers depending on their sales turnover,
  * classifying cities based on the number of inhabitants,
  * mapping booking dates to accounting periods,
  * grouping of measured values in discrete ranges.
"""


# standard library imports
from collections import Mapping, Callable

# local import
from .interval_chain import IntervalChain


__metaclass__ = type


class IntervalMapping(Mapping, Callable):

    """An IntervalMapping is a container of associated interval / value pairs.

    It is constructed from either
      * an IntervalChain and a sequence of associated values,
      * a sequence of limiting values and a sequence of associated values,
      * a sequence of tuples, each holding a limiting value and an associated
        value.

    **1. Form**

    Args:
        arg0 (:class:`IntervalChain`): sequence of intervals to be mapped
        arg1 (`Sequence`): sequence of associated values

    **2. Form**

    Args:
        arg0 (`Sequence`): sequence of values limiting the intervals to be
            mapped
        arg1 (`Sequence`): sequence of associated values

    **3. Form**

    Args:
        arg0 (`Sequence`): sequence of tuples containing a limiting value and
            an associated value

    If no IntervalChain is given, the given limiting values must be comparable
    and must be given in ascending order.

    Returns:
        instance of :class:`IntervalMapping`

    Raises:
        AssertionError: given sequences do not have the same length
        AssertionError: given sequences of limiting values is empty
        InvalidInterval: given limits do not define a sequence of adjacent
            intervals
        TypeError: given sequence is not a sequence of 2-tuples
        TypeError: wrong number of arguments
    """

    def __init__(self, *args):
        nargs = len(args)
        if nargs == 2:
            keys, vals = args
            assert len(keys) == len(vals), \
                "The given sequences must be of equal length."
            if not isinstance(keys, IntervalChain):
                assert len(keys) > 0, \
                    "The given sequences must not be empty."
                keys = IntervalChain(keys)
        elif nargs == 1:
            try:
                limits = [t[0] for t in args[0]]
                vals = [t[1] for t in args[0]]
            except (TypeError, IndexError):
                raise TypeError("Expected a sequence of 2-tuples.")
            keys = IntervalChain(limits)
        else:
            raise TypeError("1 or 2 arguments expected, got %s." % nargs)
        # interval chains are immutable, so no need to store a copy here, ...
        self._keys = keys
        # ... but the value sequence has to be copied
        self._vals = tuple(vals)

    def map(self, val):
        """Return the value associated with interval which contains `val`.
        """
        try:
            idx = self._keys.map2idx(val)
        except ValueError:
            raise KeyError("%s not in %s."
                           % (val, self._keys.total_interval))
        else:
            return self._vals[idx]

    def __call__(self, val):
        """Return the value associated with interval which contains `val`.
        """
        return self.map(val)

    def __copy__(self):
        """Return self (IntervalMapping instances are immutable)."""
        return self

    def __eq__(self, other):
        """self == other"""
        if isinstance(other, IntervalMapping):
            # interval mappings are equal if their intervals and values are
            # equal
            return self is other or (self._keys == other._keys and
                                     self._vals == other._vals)
        return NotImplemented

    def __getitem__(self, key):
        """self[key]"""
        try:
            idx = self._keys.index(key)
        except ValueError:
            raise KeyError("%s not in %s." % (key, self._keys))
        else:
            return self._vals[idx]

    def __iter__(self):
        """iter(self)"""
        return iter(self._keys)

    def __len__(self):
        """len(self)"""
        return len(self._keys)
