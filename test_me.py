#!/usr/bin/env python

# Copyright (c) 2015 Xi Wang
#
# This file is part of the UW CSE 551 lecture code.  It is freely
# distributed under the MIT License.

"""
This resembles Section 2.4 of the DART paper (PLDI'05).
"""

"""
hzy:
- Read http://kqueue.org/blog/2015/05/26/mini-mc/ to understand the program 
"""

from mc import *

def test_me(x, y):
  z = 2 * x
  if z == y:
    if y == x + 10:
      assert False

x = BitVec("x", 32) # hzy: symbolic 32-bit integers (Z3's python api)
y = BitVec("y", 32)
test_me(x, y)
#mc_fuzz(lambda: test_me(x, y), [x, y], [0, 0])
