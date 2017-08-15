#!/usr/bin/env python
# ----------------------------------------------------------------------------
# Name:        test_interval_chain
# Purpose:     Test driver for module interval_chain
#
# Author:      Michael Amrhein (michael@adrhinum.de)
#
# Copyright:   (c) Michael Amrhein
# ----------------------------------------------------------------------------
# $Source$
# $Revision$


import unittest
from copy import copy, deepcopy
from operator import delitem, setitem
from ivalutils.interval import (Interval, LowerOpenInterval,
                                LowerInfiniteLimit, UpperInfiniteLimit,
                                LowerClosedLimit, LowerOpenLimit,
                                UpperClosedLimit, UpperOpenLimit,)
from ivalutils.interval_chain import IntervalChain, EmptyIntervalChain


class IntervalChainTests(unittest.TestCase):

    def test_constructor(self):
        limits = (0, 10, 50, 300)
        min_n_ivals = len(limits) - 1
        for add_lower_inf in (True, False):
            for add_upper_inf in (True, False):
                n_ivals = min_n_ivals + (int(add_lower_inf) +
                                         int(add_upper_inf))
                for lower_closed in (True, False):
                    ic = IntervalChain(limits,
                                       lower_closed=lower_closed,
                                       add_lower_inf=add_lower_inf,
                                       add_upper_inf=add_upper_inf)
                    self.assertEqual(ic.limits, limits)
                    self.assertEqual(len(ic), n_ivals)
                    self.assertEqual(ic.is_lower_infinite(), add_lower_inf)
                    self.assertEqual(ic.is_upper_infinite(), add_upper_inf)
                    self.assertEqual(ic[1].lower_limit.is_closed(),
                                     lower_closed)
                    if add_lower_inf:
                        lower_limit = LowerInfiniteLimit()
                    elif lower_closed:
                        lower_limit = LowerClosedLimit(limits[0])
                    else:
                        lower_limit = LowerOpenLimit(limits[0])
                    if add_upper_inf:
                        upper_limit = UpperInfiniteLimit()
                    elif lower_closed:
                        upper_limit = UpperOpenLimit(limits[-1])
                    else:
                        upper_limit = UpperClosedLimit(limits[-1])
                    self.assertEqual(ic.total_interval,
                                     Interval(lower_limit, upper_limit))
                    ivals = ic._ivals
                    for idx in range(len(ivals) - 1):
                        self.assertTrue(ic[idx].is_adjacent(ic[idx + 1]))
        # limits that do not define any interval:
        self.assertRaises(EmptyIntervalChain, IntervalChain, ())
        self.assertRaises(EmptyIntervalChain,
                          IntervalChain, (3,), add_upper_inf=False)

    def test_if_immutable(self):
        limits = [0, 10, 50, 300]
        ic = IntervalChain(limits)
        self.assertRaises(TypeError, delitem, ic, 0)
        self.assertRaises(TypeError, setitem, ic, 0, 5)
        self.assertEqual(ic.limits, tuple(limits))
        del limits[0]
        self.assertNotEqual(ic.limits, tuple(limits))

    def test_copy(self):
        limits = (0, 10, 50, 300)
        ic = IntervalChain(limits)
        self.assertIs(copy(ic), ic)
        self.assertIsNot(deepcopy(ic), ic)

    def test_sequence(self):
        limits = [0, 10, 50, 300]
        ic = IntervalChain(limits)
        self.assertEqual(len(ic), len(limits))
        for idx in range(len(ic)):
            self.assertEqual(ic[idx].lower_limit.value, limits[idx])
        for idx, ival in enumerate(ic):
            self.assertEqual(ival.lower_limit.value, limits[idx])
        for idx, ival in enumerate(ic):
            self.assertEqual(idx, ic.index(ival))
        for ival in ic:
            self.assertTrue(ival in ic)
            self.assertEqual(ic.count(ival), 1)
        self.assertRaises(IndexError, ic.__getitem__, 6)
        self.assertFalse(LowerOpenInterval(0) in ic)
        idx = len(limits)
        for ival in reversed(ic):
            idx -= 1
            self.assertEqual(ival.lower_limit.value, limits[idx])

    def test_map2idx(self):
        # upper end infinite
        ic = IntervalChain(range(0, 1001, 5))
        self.assertRaises(ValueError, ic.map2idx, -4)
        self.assertEqual(ic.map2idx(2), 0)
        self.assertEqual(ic.map2idx(200), 40)
        self.assertEqual(ic.map2idx(2133), 200)
        # lower end infinite
        ic = IntervalChain(range(0, 1001, 5),
                           add_lower_inf=True, add_upper_inf=False)
        self.assertEqual(ic.map2idx(-4), 0)
        self.assertEqual(ic.map2idx(2), 1)
        self.assertEqual(ic.map2idx(200), 41)
        self.assertRaises(ValueError, ic.map2idx, 1003)
        # both ends infinite
        ic = IntervalChain(range(0, 1001, 5), add_lower_inf=True)
        self.assertEqual(ic.map2idx(-4), 0)
        self.assertEqual(ic.map2idx(2), 1)
        self.assertEqual(ic.map2idx(200), 41)
        self.assertEqual(ic.map2idx(2133), 201)
        # no end inifinite
        ic = IntervalChain(range(0, 1001, 5), add_upper_inf=False)
        self.assertRaises(ValueError, ic.map2idx, -4)
        self.assertEqual(ic.map2idx(328), 65)
        self.assertRaises(ValueError, ic.map2idx, 1003)

    def test_eq(self):
        limits = (0, 10, 50, 300)
        ic1 = IntervalChain(limits)
        self.assertEqual(ic1, ic1)
        ic2 = IntervalChain(limits)
        self.assertEqual(ic1, ic2)
        ic2 = IntervalChain(limits, lower_closed=False)
        self.assertNotEqual(ic1, ic2)
        ic2 = IntervalChain(limits, add_lower_inf=True)
        self.assertNotEqual(ic1, ic2)
        ic2 = IntervalChain(limits, add_upper_inf=False)
        self.assertNotEqual(ic1, ic2)

    def test_repr(self):
        limits = (0, 10, 50, 300)
        # lower_closed=True, add_lower_inf=False, add_upper_inf=True
        ic = IntervalChain(limits)
        r = repr(ic)
        self.assertEqual(ic, eval(r))
        # lower_closed=False, add_lower_inf=False, add_upper_inf=True
        ic = IntervalChain(limits, lower_closed=False)
        r = repr(ic)
        self.assertEqual(ic, eval(r))
        # lower_closed=True, add_lower_inf=True, add_upper_inf=True
        ic = IntervalChain(limits, add_lower_inf=True)
        r = repr(ic)
        self.assertEqual(ic, eval(r))
        # lower_closed=True, add_lower_inf=True, add_upper_inf=False
        ic = IntervalChain(limits, add_lower_inf=True, add_upper_inf=False)
        r = repr(ic)
        self.assertEqual(ic, eval(r))
        # lower_closed=True, add_lower_inf=False, add_upper_inf=False
        ic = IntervalChain(limits, add_lower_inf=False, add_upper_inf=False)
        r = repr(ic)
        self.assertEqual(ic, eval(r))


if __name__ == '__main__':
    unittest.main()
