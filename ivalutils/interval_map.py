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


"""Mappings on intervals"""


#TODO: enhance doc

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
    """

    def __init__(self, *args):
        """Initialize instance of IntervalMapping.
        """
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
        """self.map(val) -> result, i.e. the value associated with interval
        which contains val.
        """
        try:
            idx = self._keys.map2idx(val)
        except ValueError:
            raise KeyError("%s not in %s."
                           % (val, self._keys.total_interval))
        else:
            return self._vals[idx]

    def __call__(self, val):
        """self(val) -> result, i.e. the value associated with interval
        which contains val.
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
