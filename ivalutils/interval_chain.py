# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Name:        interval_chain
# Purpose:     Sequences of adjacent intervals
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


"""Sequences of adjacent intervals"""


#TODO: enhance doc

# standard library imports
from collections import Sequence

# local import
from .interval import (ChainableInterval, Interval, InvalidInterval,
                       LowerClosedInterval, LowerOpenInterval,
                       UpperClosedInterval, UpperOpenInterval)


__metaclass__ = type


class EmptyIntervalChain(Exception):

    """Raised when an empty IntervalChain would be created."""


class IntervalChain(Sequence):

    """An IntervalChain is a list of adjacent intervals.

    It is constructed from a list of limiting values.

    Args:
        limits (Iterable): an iterable of the limiting values, must be
            ordered from smallest to greatest
        lower_closed (boolean): defines which endpoint of the contained
            intervals will be closed: if `True`, lower endpoint closed, upper
            open (default), if `False`, lower endpoint open, upper closed
        add_lower_inf (boolean): defines whether a lower infinite interval
            will be added as first interval: if `True`, infinite interval as
            lowest interval, if `False`, no infinite interval as lowest
            interval (default)
        add_upper_inf (boolean): defines whether an upper infinite interval
            will be added as last interval: if `True`, infinite interval as
            last interval (default), if `False`, no infinite interval as last
            interval

    Returns:
        instance of :class:`IntervalChain`

    Raises:
        EmptyIntervalChain: given limits do not define any interval
    """

    def __init__(self, limits, lower_closed=True, add_lower_inf=False,
                 add_upper_inf=True):
        n = len(limits)
        if n == 0 or (n == 1 and not add_lower_inf and not add_upper_inf):
            raise EmptyIntervalChain(
                "Given limits do not define any interval.")
        # the iterable 'limits' needs to be copied
        self._limits = tuple(limits)
        self._lower_closed = lower_closed
        ivals = []
        if add_lower_inf:
            # add lower infinite interval
            if lower_closed:
                ivals.append(UpperOpenInterval(limits[0]))
            else:
                ivals.append(UpperClosedInterval(limits[0]))
            self._lower_inf = True
        else:
            self._lower_inf = False
        # create chainable interval from values in limits
        try:
            ivals.extend([ChainableInterval(lower_value, upper_value,
                                            lower_closed=lower_closed)
                          for (lower_value, upper_value)
                          in zip(limits[:-1], limits[1:])])
        except InvalidInterval:
            raise InvalidInterval("Limits must be given in ascending order.")
        if add_upper_inf:
            # add upper infinite interval
            if lower_closed:
                ivals.append(LowerClosedInterval(limits[-1]))
            else:
                ivals.append(LowerOpenInterval(limits[-1]))
            self._upper_inf = True
        else:
            self._upper_inf = False
        self._ivals = ivals

    @property
    def limits(self):
        """The limiting values."""
        return self._limits

    @property
    def total_interval(self):
        """Returns the interval between lower endpoint of first interval in
        self and upper endpoint of last interval in self."""
        return Interval(self[0].lower_limit, self[-1].upper_limit)

    def is_lower_infinite(self):
        """True if first interval is lower infinite."""
        return self._lower_inf

    def is_upper_infinite(self):
        """True if last interval is upper infinite."""
        return self._upper_inf

    def map2idx(self, value):
        #TODO: find better name
        """Return the index of the interval which contains value.

        Raises ValueError if value is not contained in any of the intervals in
        self."""
        n = len(self)
        # using binary search
        left, right = (0, n - 1)
        while left <= right:
            idx = (right + left) // 2
            ival = self[idx]
            if value in ival:
                return idx
            if value < ival.lower_limit:
                right = idx - 1
            else:
                left = idx + 1
        raise ValueError("%r not in any interval of %r." % (value, self))

    def __copy__(self):
        """Return self (IntervalChain instances are immutable)."""
        return self

    def __eq__(self, other):
        """self == other"""
        if isinstance(other, IntervalChain):
            # interval chains are equal if their intervals are equal
            return self is other or self._ivals == other._ivals
        return NotImplemented

    def __getitem__(self, idx):
        """self[idx]"""
        return self._ivals[idx]

    def __iter__(self):
        """iter(self)"""
        return iter(self._ivals)

    def __len__(self):
        """len(self)"""
        return len(self._ivals)

    def __repr__(self):
        """repr(self)"""
        kwds = '' if self._lower_closed else ", lower_closed=False"
        if self.is_lower_infinite():
            kwds += ", add_lower_inf=True"
        if not self.is_upper_infinite():
            kwds += ", add_upper_inf=False"
        return "%s(%s%s)" % (self.__class__.__name__, self.limits, kwds)

    def __str__(self):
        """str(self)"""
        return '[%s]' % ', '.join([str(i) for i in self])
