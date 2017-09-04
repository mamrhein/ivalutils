# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Name:        interval
# Purpose:     Basic interval arithmetic
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


"""Basic interval arithmetic.

Usage
=====

Creating intervals
------------------

The class :class:`Interval` is used to create intervals, i. e. subsets of a
set of values, by defining a lower and an upper endpoint.

The simplest way is calling :class:`Interval` without arguments, resulting in
both endpoints to be infinite:

    >>> ival = Interval()
    >>> ival
    Interval()
    >>> str(ival)
    '(-inf .. +inf)'

For getting a more useful interval, it's neccessary to specify atleast one
endpoint:

    >>> ival = Interval(LowerClosedLimit(0))
    >>> ival
    Interval(lower_limit=Limit(True, 0, True))
    >>> str(ival)
    '[0 .. +inf)'

    >>> ival = Interval(upper_limit=UpperClosedLimit(100.))
    >>> ival
    Interval(upper_limit=Limit(False, 100.0, True))
    >>> str(ival)
    '(-inf .. 100.0]'

    >>> ival = Interval(LowerClosedLimit(0), UpperOpenLimit(27))
    >>> ival
    Interval(lower_limit=Limit(True, 0, True), upper_limit=Limit(False, 27, \
False))
    >>> str(ival)
    '[0 .. 27)'

Any type which defines a total ordering can be used for the limits:

    >>> ClosedInterval('a', 'zzz')
    Interval(lower_limit=Limit(True, 'a', True), upper_limit=Limit(False, \
'zzz', True))

Several factory functions can be used as shortcut. For example:

    >>> LowerClosedInterval(30)
    Interval(lower_limit=Limit(True, 30, True))
    >>> UpperOpenInterval(0)
    Interval(upper_limit=Limit(False, 0, False))
    >>> ClosedInterval(1, 3)
    Interval(lower_limit=Limit(True, 1, True), upper_limit=Limit(False, 3, \
True))
    >>> ChainableInterval(0, 5)
    Interval(lower_limit=Limit(True, 0, True), upper_limit=Limit(False, 5, \
False))

Operations on intervals
-----------------------

The limits of an interval can be retrieved via properties:

    >>> ival = ClosedInterval(0, 100)
    >>> ival.lower_limit
    Limit(True, 0, True)
    >>> ival.upper_limit
    Limit(False, 100, True)
    >>> ival.limits
    (Limit(True, 0, True), Limit(False, 100, True))

Several methods can be used to test for specifics of an interval. For example:

    >>> ival.is_bounded()
    True
    >>> ival.is_finite()
    True
    >>> ival.is_left_open()
    False

Intervals can be tested for including a value:

    >>> 74 in ival
    True
    >>> -4 in ival
    False

Intervals can be compared:

    >>> ival2 = LowerOpenInterval(100)
    >>> ival3 = LowerClosedInterval(100)
    >>> ival < ival2
    True
    >>> ival < ival3
    True
    >>> ival2 < ival3
    False
    >>> ival2 == ival3
    False
    >>> ival3 < ival2
    True
    >>> ival2.is_adjacent(ival3)
    False
    >>> ival3.is_adjacent(ival2)
    False
    >>> ival4 = UpperClosedInterval(100)
    >>> ival4.is_adjacent(ival2)
    True
    >>> ival.is_overlapping(ival3)
    True
    >>> ival.is_subset(ival4)
    True
"""


# standard library imports
from collections import Container
from functools import total_ordering
import operator


__metaclass__ = type


LOWER_LIMIT_SYMBOLS = ['(', '[']
UPPER_LIMIT_SYMBOLS = [')', ']']
INFINITY_SYMBOL = 'inf'
INTERVAL_SYMBOL = '..'
#???: should we use unicode symbols?
#INFINITY_SYMBOL = '∞'
#INTERVAL_SYMBOL = '…'


# --- Exceptions ---

class IncompatibleLimits(TypeError):

    """Raised when comparing limits with incompatible types of values."""


class InvalidInterval(Exception):

    """Raised when an invalid Interval would be created."""


# --- Handling infinity ---

class _Inf:

    """Value representing infinity."""

    __slots__ = ()

    symbol = INFINITY_SYMBOL

    def __new__(cls):
        try:
            return cls._the_one_and_only
        except AttributeError:
            inf = object.__new__(cls)
            cls._the_one_and_only = inf
            return inf

    def __repr__(self):
        return "%s()" % self.__class__.__name__         # pragma: no cover

    def __str__(self):
        return self.symbol


@total_ordering
class Inf(_Inf):

    """Value representing (positive) infinity."""

    symbol = '+' + INFINITY_SYMBOL

    def __eq__(self, other):
        # singletons can savely be compared by identity
        return other is self

    # needed in Python 3.x:
    __hash__ = object.__hash__

    # there's nothing greater
    __le__ = __eq__


@total_ordering
class NegInf(_Inf):

    """Value representing negative infinity."""

    symbol = '-' + INFINITY_SYMBOL

    def __eq__(self, other):
        # singletons can savely be compared by identity
        return other is self

    # needed in Python 3.x:
    __hash__ = object.__hash__

    # there's nothing smaller
    __ge__ = __eq__


# --- Limits ---

class AbstractLimit:

    """Abstract base class of a Limit."""

    __slots__ = ()

    # used to map (is_lower, is_closed) to operator in method is_observed_by
    _ops = ((operator.lt, operator.le), (operator.gt, operator.ge))

    def __init__(self):                                 # pragma: no cover
        raise NotImplementedError

    def is_lower(self):
        """True if self is lower endpoint, False otherwise."""
        return self._lower

    def is_upper(self):
        """True if self is upper endpoint, False otherwise."""
        return not self.is_lower()

    @property
    def value(self):
        """The limiting value."""
        return self._value

    def is_observed_by(self, value):
        """True if value does not exceed the limit."""
        op = self._ops[self.is_lower()][self.is_closed()]
        return op(value, self.value)

    def is_closed(self):
        """True if self is closed endpoint, False otherwise."""
        return self._closed

    def is_open(self):
        """True if self is open endpoint, False otherwise."""
        return not self.is_closed()

    def is_lower_adjacent(self, other):
        """True if self < other and Interval(self, other) is empty."""
        return self < other and self.value == other.value

    def is_upper_adjacent(self, other):
        """True if self > other and Interval(other, self) is empty."""
        return self > other and self.value == other.value

    def is_adjacent(self, other):
        """True if self.is_lower_adjacent(other) or
        self.is_upper_adjacent(other)."""
        return self.is_lower_adjacent(other) or self.is_upper_adjacent(other)

    def adjacent_limit(self):                           # pragma: no cover
        """Return the limit adjacent to self."""
        raise NotImplementedError

    def __copy__(self):
        """Return self (Limit instances are immutable)."""
        return self

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __str__(self):
        value = self.value
        if isinstance(value, (bytes, str)):
            value = "'%s'" % value
        if self.is_lower():
            return "%s%s" % (LOWER_LIMIT_SYMBOLS[self.is_closed()], value)
        else:
            return "%s%s" % (value, UPPER_LIMIT_SYMBOLS[self.is_closed()])


@total_ordering
class InfiniteLimit(AbstractLimit):

    """Lower / upper limit of an unbounded (aka infinite) Interval.

    Args:
        lower (bool): specifies which endpoint of an interval this limit
            defines: `True` -> lower endpoint, `False` -> upper endpoint

    Returns:
        instance of :class:`InfiniteLimit`

    Raises:
        AssertionError: `lower` is not instance of `bool`
    """

    __slots__ = ['_lower']

    # dict holding singletons for lower and upper infinite limit
    _singletons = {}

    def __new__(cls, lower):
        assert isinstance(lower, bool)
        try:
            return cls._singletons[lower]
        except KeyError:
            inf = super(InfiniteLimit, cls).__new__(cls)
            cls._singletons[lower] = inf
            return inf

    def __init__(self, lower):
        self._lower = lower

    @property
    def value(self):
        """Lower / upper infinity."""
        if self.is_lower():
            return NegInf()
        else:
            return Inf()

    def is_closed(self):
        """False (infinite endpoints is always open)."""
        return False

    def adjacent_limit(self):
        """Return None because an infinite limit has no adjacent limit."""
        return None

    def __hash__(self):
        """hash(self)"""
        return hash((self.is_lower(), self.value, False))

    def __eq__(self, other):
        """self == other"""
        # singletons can savely be compared by identity
        return other is self

    def __lt__(self, other):
        """self < other"""
        # self is lower limit => self.value == NegInf and
        # self is upper limit => self.value == Inf,
        # so we can savely delegate comparison to the values
        try:
            return self.value < other.value
        except AttributeError:
            # other is not a Limit, so take it as value
            return self.value < other

    def __repr__(self):                                 # pragma: no cover
        return "%sInfiniteLimit()" % ['Upper', 'Lower'][self.is_lower()]


# Two factory functions for creating the infinite limits

def LowerInfiniteLimit():
    """Create a lower infinite limit (a singleton)."""
    return InfiniteLimit(True)


def UpperInfiniteLimit():
    """Create an upper infinite limit (a singleton)."""
    return InfiniteLimit(False)


class Limit(AbstractLimit):

    """Lower / upper limit of an Interval.

    Args:
        lower (bool): specifies which endpoint of an interval this limit
            defines: `True` -> lower endpoint, `False` -> upper endpoint
        value (<total ordering>): limiting value (can be of any type that
            defines a total ordering)
        closed (bool): specifies whether value itself is the endpoint or not:
            `True` -> the interval that has this limit includes value,
            `False` -> the interval that has this limit does not includes
            value

    Returns:
        instance of :class:`Limit`

    Raises:
        AssertionError: `lower` is not instance of `bool`
        AssertionError: `value` is None
        AssertionError: `closed` is not instance of `bool`
    """

    __slots__ = ['_lower', '_value', '_closed']

    def __init__(self, lower, value, closed=True):
        assert isinstance(lower, bool)
        # prevent undefined limit
        assert value is not None
        # for infinite limit use InfiniteLimit
        assert not isinstance(value, _Inf)
        #???: Check whether type of value defines an ordering?
        assert isinstance(closed, bool)
        self._lower = lower
        self._value = value
        self._closed = closed

    def _map_limit_type(self):
        # upper+open < closed < lower+open
        if self.is_closed():
            return 0
        if self.is_lower():
            return 1
        return -1

    def _compare(self, other, op):
        if isinstance(other, Limit):
            self_val, other_val = self.value, other.value
            try:
                if self_val == other_val:
                    # if limit values are equal, result depends on limit types
                    return op(self._map_limit_type(), other._map_limit_type())
                return op(self_val, other_val)
            except TypeError as exc:
                raise IncompatibleLimits(*exc.args)
        else:
            self_val = self.value
            try:
                # is other comparable to self.value?
                if self_val == other:
                    # if values are equal, result depends on limit type
                    return op(self._map_limit_type(), 0)
                return op(self_val, other)
            except TypeError:                           # pragma: no cover
                return NotImplemented

    def adjacent_limit(self):
        """Return the limit adjacent to self."""
        return Limit(not self.is_lower(), self.value, not self.is_closed())

    def __hash__(self):
        """hash(self)"""
        return hash((self.is_lower(), self.value, self.is_closed()))

    def __eq__(self, other):
        """self == other"""
        return self._compare(other, operator.eq)

    def __lt__(self, other):
        """self < other"""
        return self._compare(other, operator.lt)

    def __le__(self, other):
        """self <= other"""
        return self._compare(other, operator.le)

    def __gt__(self, other):
        """self > other"""
        return self._compare(other, operator.gt)

    def __ge__(self, other):
        """self >= other"""
        return self._compare(other, operator.ge)

    def __repr__(self):                                 # pragma: no cover
        return "%s(%s, %s, %s)" % (self.__class__.__name__,
                                   self.is_lower(),
                                   repr(self.value),
                                   self.is_closed())


# Some factory functions for creating limits

def LowerLimit(value, closed=True):
    """Create a lower limit.

    Args:
        value (<total ordering>): limiting value (can be of any type that
            defines a total ordering)
        closed (bool): specifies whether value itself is the endpoint or not:
            `True` -> the interval that has this limit includes value,
            `False` -> the interval that has this limit does not includes
            value

    Returns:
        instance of :class:`Limit`

    Raises:
        AssertionError: `value` is None
        AssertionError: `closed` is not instance of `bool`
    """
    return Limit(True, value, closed)


def UpperLimit(value, closed=True):
    """Create an upper limit.

    Args:
        value (<total ordering>): limiting value (can be of any type that
            defines a total ordering)
        closed (bool): specifies whether value itself is the endpoint or not:
            `True` -> the interval that has this limit includes value,
            `False` -> the interval that has this limit does not includes
            value

    Returns:
        instance of :class:`Limit`

    Raises:
        AssertionError: `value` is None
        AssertionError: `closed` is not instance of `bool`
    """
    return Limit(False, value, closed)


def LowerClosedLimit(value):
    """Create a lower closed limit.

    Args:
        value (<total ordering>): limiting value (can be of any type that
            defines a total ordering)

    Returns:
        instance of :class:`Limit`

    Raises:
        AssertionError: `value` is None
    """
    return Limit(True, value, closed=True)


def LowerOpenLimit(value):
    """Create a lower open limit.

    Args:
        value (<total ordering>): limiting value (can be of any type that
            defines a total ordering)

    Returns:
        instance of :class:`Limit`

    Raises:
        AssertionError: `value` is None
    """
    return Limit(True, value, closed=False)


def UpperClosedLimit(value):
    """Create an upper closed limit.

    Args:
        value (<total ordering>): limiting value (can be of any type that
            defines a total ordering)

    Returns:
        instance of :class:`Limit`

    Raises:
        AssertionError: `value` is None
    """
    return Limit(False, value, closed=True)


def UpperOpenLimit(value):
    """Create an upper open limit.

    Args:
        value (<total ordering>): limiting value (can be of any type that
            defines a total ordering)

    Returns:
        instance of :class:`Limit`

    Raises:
        AssertionError: `value` is None
    """
    return Limit(False, value, closed=False)


# --- Intervals ---

class Interval(Container):

    """An Interval defines a subset of a set of values by optionally giving
    a lower and / or an upper limit.

    The base set of values - and therefore the given limits - must have a
    common base type which defines a total order on the values.

    If both limits are given, the interval is said to be *bounded* or
    *finite*, if only one or neither of them is given, the interval is said
    to be *unbounded* or *infinite*.

    If only the lower limit is given, the interval is called *lower bounded*
    or *left bounded* (maybe also *upper unbounded*, *upper infinite*,
    *right unbounded* or *right infinite*). Correspondingly, if only the
    upper limit is given, the interval is called *upper bounded*
    or *right bounded* (maybe also *lower unbounded*, *lower infinite*,
    *left unbounded* or *left infinite*).

    For both limits (aka endpoints) must be specified whether the given value
    is included in the interval or not. In the first case the limit is called
    *closed*, otherwise *open*.

    Args:
        lower_limit (:class:`Limit`): lower limit (default: None)
        upper_limit (:class:`Limit`): upper limit (default: None)

    Returns:
        instance of :class:`Interval`

    If `None` is given as `lower_limit`, the resulting interval is lower
    infinite. If `None` is given as `upper_limit`, the resulting interval is
    upper infinite.

    Raises:
        InvalidInterval: `lower_limit` is not a lower limit
        InvalidInterval: `upper_limit` is not a upper limit
        InvalidInterval: `lower_limit` > `upper_limit`
        IncompatibleLimits: values of `lower_limit` and `upper_limit` are not
            comparable
    """

    def __init__(self, lower_limit=None, upper_limit=None):
        if lower_limit is not None and lower_limit != LowerInfiniteLimit():
            if lower_limit.is_upper():
                raise InvalidInterval("Given lower limit is an upper limit.")
            self._lower_limit = lower_limit
        if upper_limit is not None and upper_limit != UpperInfiniteLimit():
            if upper_limit.is_lower():
                raise InvalidInterval("Given upper limit is a lower limit.")
            self._upper_limit = upper_limit
        if self.lower_limit > self.upper_limit:
            raise InvalidInterval("Given lower limit > given upper limit.")

    @property
    def lower_limit(self):
        """Lower limit (LowerInfiniteLimit, if no lower limit was given.)"""
        try:
            return self._lower_limit
        except AttributeError:
            return LowerInfiniteLimit()

    @property
    def upper_limit(self):
        """Upper limit (UpperInfiniteLimit, if no upper limit was given.)"""
        try:
            return self._upper_limit
        except AttributeError:
            return UpperInfiniteLimit()

    @property
    def _limits(self):
        limits = []
        try:
            limits.append(self._lower_limit)
        except AttributeError:
            pass
        try:
            limits.append(self._upper_limit)
        except AttributeError:
            pass
        return limits

    @property
    def limits(self):
        """Lower and upper limit as tuple."""
        return (self.lower_limit, self.upper_limit)

    def is_lower_bounded(self):
        try:
            return self._lower_limit and True
        except AttributeError:
            return False
    # alternate name
    is_left_bounded = is_lower_bounded

    def is_upper_bounded(self):
        try:
            return self._upper_limit and True
        except AttributeError:
            return False
    # alternate name
    is_right_bounded = is_upper_bounded

    def is_bounded(self):
        return self.is_lower_bounded() and self.is_upper_bounded()
    # alternate name
    is_finite = is_bounded

    def is_lower_unbounded(self):
        return not self.is_lower_bounded()

    def is_upper_unbounded(self):
        return not self.is_upper_bounded()

    def is_unbounded(self):
        return self.is_lower_unbounded() or self.is_upper_unbounded()
    # alternate name
    is_infinite = is_unbounded

    def is_lower_closed(self):
        return self.lower_limit.is_closed()
    # alternate name
    is_left_closed = is_lower_closed

    def is_upper_closed(self):
        return self.upper_limit.is_closed()
    # alternate name
    is_right_closed = is_upper_closed

    def is_closed(self):
        return self.is_lower_closed() and self.is_upper_closed()

    def is_lower_open(self):
        return self.lower_limit.is_open()
    # alternate name
    is_left_open = is_lower_open

    def is_upper_open(self):
        return self.upper_limit.is_open()
    # alternate name
    is_right_open = is_upper_open

    def is_open(self):
        return self.is_lower_open() or self.is_upper_open()

    def __contains__(self, value):
        """True if value does not exceed the limits of self."""
        return all((limit.is_observed_by(value) for limit in self._limits))

    def __eq__(self, other):
        """self == other.

        True if all elements contained in self are also contained in other
        and all elements contained in other are also contained in self.

        This is exactly the case if self.limits == other.limits."""
        if isinstance(other, Interval):
            return self.limits == other.limits
        return NotImplemented

    def __lt__(self, other):
        """self < other.

        True if there is an element in self which is smaller than all
        elements in other or there is an element in other which is greater
        than all elements in self.

        This is exactly the case if self.limits < other.limits."""
        if isinstance(other, Interval):
            return self.limits < other.limits
        return NotImplemented

    def __le__(self, other):
        """self <= other."""
        if isinstance(other, Interval):
            return self.limits <= other.limits
        return NotImplemented

    def __gt__(self, other):
        """self > other.

        True if there is an element in self which is greater than all
        elements in other or there is an element in other which is smaller
        than all elements in self.

        This is exactly the case if self.limits > other.limits."""
        if isinstance(other, Interval):
            return self.limits > other.limits
        return NotImplemented

    def __ge__(self, other):
        """self >= other."""
        if isinstance(other, Interval):
            return self.limits >= other.limits
        return NotImplemented

    def is_subset(self, other):
        """True if self defines a proper subset of other, i.e. all elements
        contained in self are also contained in other, but not the other way
        round."""
        return (self.lower_limit >= other.lower_limit and
                self.upper_limit <= other.upper_limit and
                self != other)

    def is_disjoint(self, other):
        """True if self contains no elements in common with other."""
        return (self.lower_limit > other.upper_limit or
                self.upper_limit < other.lower_limit)

    def is_overlapping(self, other):
        """True if there is a common element in self and other."""
        return not self.is_disjoint(other)

    def is_lower_adjacent(self, other):
        """True if self.upper_limit.is_lower_adjacent(other.lower_limit)."""
        return self.upper_limit.is_lower_adjacent(other.lower_limit)

    def is_upper_adjacent(self, other):
        """True if self.lower_limit.is_upper_adjacent(other.upper_limit)."""
        return self.lower_limit.is_upper_adjacent(other.upper_limit)

    def is_adjacent(self, other):
        """True if self.is_lower_adjacent(other) or
        self.is_upper_adjacent(other)."""
        return self.is_lower_adjacent(other) or self.is_upper_adjacent(other)

    def __and__(self, other):
        """self & other"""
        if isinstance(other, Interval):
            if self.is_disjoint(other):
                raise InvalidInterval("Intervals are disjoint, " +
                                      "so intersection is not an Interval.")
            lower_limit = max(self.lower_limit, other.lower_limit)
            upper_limit = min(self.upper_limit, other.upper_limit)
            return Interval(lower_limit, upper_limit)
        return NotImplemented

    def __or__(self, other):
        """self | other"""
        if isinstance(other, Interval):
            if self.is_overlapping(other) or self.is_adjacent(other):
                lower_limit = min(self.lower_limit, other.lower_limit)
                upper_limit = max(self.upper_limit, other.upper_limit)
                return Interval(lower_limit, upper_limit)
            raise InvalidInterval("Intervals are disjoint and not adjacent, "
                                  "so union is not an Interval")
        return NotImplemented

    def __sub__(self, other):
        """self - other"""
        if isinstance(other, Interval):
            if self.lower_limit >= other.lower_limit:
                if self.upper_limit <= other.upper_limit:
                    raise InvalidInterval("self is subset of other, "
                                          "so result is not an Interval.")
                else:
                    lower_limit = max(self.lower_limit,
                                      other.upper_limit.adjacent_limit())
                    upper_limit = self.upper_limit
            else:
                if self.upper_limit <= other.upper_limit:
                    lower_limit = self.lower_limit
                    upper_limit = min(self.upper_limit,
                                      other.lower_limit.adjacent_limit())
                else:
                    raise InvalidInterval("other is subset of self, "
                                          "so result is not an Interval.")
            return Interval(lower_limit, upper_limit)
        return NotImplemented

    def __hash__(self):
        """hash(self)"""
        return hash(self.limits)

    def __copy__(self):
        """Return self (Interval instances are immutable)."""
        return self

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __repr__(self):
        params = ["%s_limit=%r" % (['upper', 'lower'][l.is_lower()], l)
                  for l in self._limits]
        return "%s(%s)" % (self.__class__.__name__, ', '.join(params))

    def __str__(self):
        return "%s %s %s" % (self.lower_limit,
                             INTERVAL_SYMBOL,
                             self.upper_limit)


# Some factory functions for creating intervals

def ClosedInterval(lower_value, upper_value):
    """Create Interval with closed endpoints."""
    return Interval(lower_limit=LowerClosedLimit(lower_value),
                    upper_limit=UpperClosedLimit(upper_value))


def OpenBoundedInterval(lower_value, upper_value):
    """Create Interval with open endpoints."""
    return Interval(lower_limit=LowerOpenLimit(lower_value),
                    upper_limit=UpperOpenLimit(upper_value))
# alternate name
OpenFiniteInterval = OpenBoundedInterval


def LowerClosedInterval(lower_value):
    """Create Interval with closed lower and infinite upper endpoint."""
    return Interval(lower_limit=LowerClosedLimit(lower_value))


def UpperClosedInterval(upper_value):
    """Create Interval with infinite lower and closed upper endpoint."""
    return Interval(upper_limit=UpperClosedLimit(upper_value))


def LowerOpenInterval(lower_value):
    """Create Interval with open lower and infinite upper endpoint."""
    return Interval(lower_limit=LowerOpenLimit(lower_value))


def UpperOpenInterval(upper_value):
    """Create Interval with infinite lower and open upper endpoint."""
    return Interval(upper_limit=UpperOpenLimit(upper_value))


def ChainableInterval(lower_value, upper_value, lower_closed=True):
    """Create Interval with one closed and one open endpoint."""
    if lower_closed:
        return Interval(lower_limit=LowerClosedLimit(lower_value),
                        upper_limit=UpperOpenLimit(upper_value))
    else:
        return Interval(lower_limit=LowerOpenLimit(lower_value),
                        upper_limit=UpperClosedLimit(upper_value))
