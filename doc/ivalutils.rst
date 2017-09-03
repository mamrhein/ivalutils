********
Interval
********

.. automodule:: ivalutils.interval

Classes
=======

.. autoclass:: Limit
    :members: adjacent_limit, __hash__, __eq__, __lt__, __le__, __gt__,
        __ge__, __repr__

.. autoclass:: Interval
    :members: lower_limit, upper_limit, limits, is_lower_bounded,
        is_left_bounded, is_upper_bounded, is_right_bounded, is_bounded,
        is_finite, is_lower_unbounded, is_upper_unbounded, is_unbounded,
        is_infinite, is_lower_closed, is_left_closed, is_upper_closed,
        is_right_closed, is_closed, is_lower_open, is_left_open,
        is_lower_adjacent, is_upper_adjacent, is_adjacent, is_upper_open,
        is_right_open, is_open, is_subset, is_disjoint, is_overlapping,
        __contains__, __eq__, __lt__, __le__, __gt__, __ge__, __and__, __or__,
        __sub__, __hash__, __copy__, __deepcopy__, __repr__, __str__

Factoryfunctions
================

.. autofunction:: LowerLimit
.. autofunction:: LowerInfiniteLimit
.. autofunction:: UpperLimit
.. autofunction:: UpperInfiniteLimit
.. autofunction:: LowerClosedLimit
.. autofunction:: LowerOpenLimit
.. autofunction:: UpperClosedLimit
.. autofunction:: UpperOpenLimit
.. autofunction:: ChainableInterval
.. autofunction:: ClosedInterval
.. autofunction:: LowerClosedInterval
.. autofunction:: LowerOpenInterval
.. autofunction:: OpenBoundedInterval
.. autofunction:: OpenFiniteInterval
.. autofunction:: UpperClosedInterval
.. autofunction:: UpperOpenInterval

Exceptions
==========

.. autoclass:: IncompatibleLimits
.. autoclass:: InvalidInterval

*************
IntervalChain
*************

.. automodule:: ivalutils.interval_chain

Classes
=======

.. autoclass:: IntervalChain
    :members: limits, total_interval, is_lower_infinite, is_upper_infinite,
        map2idx, __copy__, __eq__, __getitem__, __iter__, __len__, __repr__,
        __str__

Exceptions
==========

.. autoclass:: EmptyIntervalChain

***************
IntervalMapping
***************

.. automodule:: ivalutils.interval_map

Classes
=======

.. autoclass:: IntervalMapping
    :members: map, __call__, __copy__, __eq__, __getitem__, __iter__, __len__
