The package `ivalutils` provides classes for basic interval arithmetics as
well as classes for building sequences of adjacent intervals and for building
mappings of intervals to arbitrary values.

An Interval defines a subset of a set of values by optionally giving a lower
and / or an upper limit.

The base set of values - and therefore the given limits - must have a
common base type which defines a total order on the values.

Creating intervals
------------------

The simplest way is calling the class `Interval` without arguments, resulting
in both endpoints to be infinite:

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

Creating sequences of adjacent intervals
----------------------------------------

The class `IntervalChain` is used to create sequences of adjacent intervals:

    >>> ic = IntervalChain(('a', 'd', 'g', 'z'))
    >>> ic
    IntervalChain(('a', 'd', 'g', 'z'))

The default is to create an interval sequence which is lower-bound and
upper-infinite and containing lower-closed intervals:

    >>> str(ic)
    "[['a' .. 'd'), ['d' .. 'g'), ['g' .. 'z'), ['z' .. +inf)]"

By specifying additional parameters, you can determine which endpoints will be
closed and whether a lower and / or upper infinite endpoint will be added:

    >>> ic = IntervalChain(('a', 'd', 'g', 'z'), lower_closed = False, \
add_lower_inf=True, add_upper_inf=False)
    >>> str(ic)
    "[(-inf .. 'a'], ('a' .. 'd'], ('d' .. 'g'], ('g' .. 'z']]"

Operations on interval chains
-----------------------------

Interval chains can be indexed and iterated like lists ...:

    >>> ic[2]
    Interval(lower_limit=Limit(True, 'd', False), upper_limit=Limit(False, \
'g', True))
    >>> [ival.upper_limit.value for ival in ic]
    ['a', 'd', 'g', 'z']

... and can be searched for the index of the interval holding a specified
value:

    >>> ic.map2idx('b')
    1
    >>> ic.map2idx('a')
    0
    >>> ic.map2idx('aa')
    1

Creating interval mappings
--------------------------

The class `IntervalMapping` is used to create a mapping from intervals to
arbitrary values.

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

For more details see the documentation on GitHub or at
http://ivalutils.readthedocs.io.
