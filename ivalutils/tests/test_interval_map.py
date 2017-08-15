#!/usr/bin/env python
# ----------------------------------------------------------------------------
# Name:        test_interval_map
# Purpose:     Test driver for module interval_map
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
from ivalutils.interval import InvalidInterval, LowerOpenInterval
from ivalutils.interval_chain import IntervalChain
from ivalutils.interval_map import IntervalMapping


class IntervalMappingTests(unittest.TestCase):

    def test_constructor(self):
        limits = (0, 10, 50, 300)
        ic = IntervalChain(limits)
        vals = ('alarming', 'low', 'medium', 'high')
        items = tuple(zip(ic, vals))
        im = IntervalMapping(ic, vals)
        self.assertIsInstance(im._keys, IntervalChain)
        self.assertEqual(im._keys, ic)
        self.assertEqual(im._vals, tuple(vals))
        self.assertEqual(tuple(im.keys()), tuple(ic))
        self.assertEqual(tuple(im.values()), tuple(vals))
        self.assertEqual(tuple(im.items()), items)
        # alternate arg
        im = IntervalMapping(list(zip(limits, vals)))
        self.assertIsInstance(im._keys, IntervalChain)
        self.assertEqual(im._keys, ic)
        self.assertEqual(im._vals, tuple(vals))
        self.assertEqual(tuple(im.keys()), tuple(ic))
        self.assertEqual(tuple(im.values()), tuple(vals))
        self.assertEqual(tuple(im.items()), items)
        # non-infinite limits
        limits = ('a', 'k', 'p', 'z')
        ic = IntervalChain(limits, add_lower_inf=False, add_upper_inf=False)
        vals = [1, 2, 3]
        items = tuple(zip(ic, vals))
        im = IntervalMapping(ic, vals)
        self.assertIsInstance(im._keys, IntervalChain)
        self.assertEqual(im._keys, ic)
        self.assertEqual(im._vals, tuple(vals))
        self.assertEqual(tuple(im.keys()), tuple(ic))
        self.assertEqual(tuple(im.values()), tuple(vals))
        self.assertEqual(tuple(im.items()), items)
        # two tuples given
        limits = (0, 10, 50, 300)
        vals = ('alarming', 'low', 'medium', 'high')
        im = IntervalMapping(limits, vals)
        self.assertIsInstance(im._keys, IntervalChain)
        self.assertEqual(tuple(im.keys()), tuple(IntervalChain(limits)))
        self.assertEqual(tuple(im.values()), vals)
        # check wrong args
        self.assertRaises(TypeError, IntervalMapping)
        self.assertRaises(TypeError, IntervalMapping, 5)
        self.assertRaises(TypeError, IntervalMapping, (5, 7, 20))
        self.assertRaises(AssertionError, IntervalMapping, (5, 7), ('a',))
        self.assertRaises(AssertionError, IntervalMapping, (), ())
        self.assertRaises(TypeError, IntervalMapping, 'abc')
        self.assertRaises(TypeError, IntervalMapping, ic)
        self.assertRaises(TypeError, IntervalMapping, ic, vals, 'abc')
        self.assertRaises(InvalidInterval, IntervalMapping,
                          [(5, 'a'), (1, 'b')])

    def test_if_immutable(self):
        limits = (0, 10, 50, 300)
        ic = IntervalChain(limits)
        vals = ['alarming', 'low', 'medium', 'high']
        im = IntervalMapping(ic, vals)
        self.assertRaises(TypeError, delitem, im, ic[0])
        self.assertRaises(TypeError, setitem, im, ic[0], 'x')
        self.assertEqual(im._vals, tuple(vals))
        del vals[0]
        self.assertNotEqual(im._vals, tuple(vals))

    def test_copy(self):
        limits = (0, 10, 50, 300)
        ic = IntervalChain(limits)
        vals = ('a', 'b', 'c', 'd')
        im = IntervalMapping(ic, vals)
        self.assertIs(copy(im), im)
        self.assertIsNot(deepcopy(im), im)

    def test_mapping(self):
        limits = (0, 10, 50, 300)
        ic = IntervalChain(limits)
        vals = ['alarming', 'low', 'medium', 'high']
        im = IntervalMapping(ic, vals)
        self.assertEqual(len(im), len(vals))
        for key in im:
            self.assertEqual(im[key], vals[ic.index(key)])
        self.assertRaises(KeyError, im.__getitem__, LowerOpenInterval(0))
        self.assertFalse(LowerOpenInterval(0) in im)
        for ival in ic:
            self.assertTrue(ival in im)

    def test_eq(self):
        limits = (0, 10, 50, 300)
        ic = IntervalChain(limits)
        vals = ('alarming', 'low', 'medium', 'high')
        im1 = IntervalMapping(ic, vals)
        self.assertEqual(im1, im1)
        im2 = IntervalMapping(ic, vals)
        self.assertEqual(im1, im2)
        # alternate arg
        tl = list(zip(limits, vals))
        im2 = IntervalMapping(tl)
        self.assertEqual(im1, im2)
        # dict holding same keys and values
        d = dict(tl)
        self.assertNotEqual(im2, d)

    def test_interval_mapping(self):
        limits = (0, 10, 50, 300)
        ic = IntervalChain(limits)
        vals = ('alarming', 'low', 'medium', 'high')
        im = IntervalMapping(ic, vals)
        self.assertEqual(im.map(5), 'alarming')
        self.assertEqual(im.map(10), 'low')
        self.assertEqual(im(500), 'high')
        self.assertRaises(KeyError, im.map, -4)
        limits = ('a', 'k', 'p', 'z')
        ic = IntervalChain(limits, add_lower_inf=False, add_upper_inf=False)
        vals = (1, 2, 3)
        im = IntervalMapping(ic, vals)
        self.assertEqual(im.map('a'), 1)
        self.assertEqual(im.map('j'), 1)
        self.assertEqual(im('y'), 3)
        self.assertRaises(KeyError, im.map, 'A')
        self.assertRaises(KeyError, im, 'z')


if __name__ == '__main__':
    unittest.main()
