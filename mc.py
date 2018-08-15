# -*- coding: utf-8 -*-

# Copyright (c) 2015 Xi Wang
#
# This file is part of the UW CSE 551 lecture code.  It is freely
# distributed under the MIT License.

# ---------------------------------------------------------------
# symbolic
# ---------------------------------------------------------------

from mc_util import *


def sched_fork(self):
    """
    hzy: the whole fork graph looks like:

    3216 -- ( 2*x == y) ------------- (y == x + 10)  ------ Assertion False
          |- 3217 ( 2*x != y) -x   |- 3218 ( y != x + 10) -x

    :param self: BoolRef
    :return: bool
    """
    pid = os.fork()
    if pid:
        # hzy: add(..) adds the constraints (i.e. the constraints have been asserted in the solver.)
        solver.add(self)
        r = True
        mc_log("assume (%s)" % (str(self),))
    else:
        # hzy: Not(..) Z3's boolean operator (negation in this case)
        solver.add(Not(self))
        r = False
        mc_log("assume ¬(%s)" % (str(self),))
    if solver.check() != sat:
        mc_log("unreachable")
        sys.exit(0)
    return r


# hzy: setattr(object, name, value)
# set 'object''s attribute ('name')'s value to 'value'
#
# Xi: as values are symbolic (e.g., via Z3’s BitVec),
# the Python VM will try to convert them into bool at if statements;
# let’s intercept the conversion and replace it with sched_fork(),
# by rewriting __bool__ (Python 3.x) or __nonzero__ (Python 2.x).
#
# hzy: inside 'test_me' function, when the program executes to if statement,
# as Xi suggested, python will try to do conversion by invoking bool(self),
# which invokes __nonzero__(self) in python2 (https://rszalski.github.io/magicmethods/)
# __bool__(self) in python3. We can overload those methods via setattr
# self contains the boolean expression (e.g. 2*x == y) which is a BoolRef object.
setattr(BoolRef, "__bool__", sched_fork)
# hzy: getattr(object, name[, default])
# return the value of the named attribute of object
setattr(BoolRef, "__nonzero__", getattr(BoolRef, "__bool__"))


# ---------------------------------------------------------------
# concolic
# ---------------------------------------------------------------

def sched_flip(self, trace):
    solver.push()
    solver.add(self)
    r = (solver.check() == sat)
    solver.pop()
    if r:
        cond = self
    else:
        cond = Not(self)
    trace.append(cond)
    mc_log("%s: %s" % (self, r))
    return r


def mc_fuzz(f, init_keys, init_vals, cnt=0):
    assert len(init_keys) == len(init_vals)
    mc_log("=" * 60)
    mc_log("#%s: %s" % (cnt, ', '.join(["%s = %s" % (k, v) for k, v in zip(init_keys, init_vals)])))

    trace = []
    setattr(BoolRef, "__bool__", lambda self: sched_flip(self, trace))
    setattr(BoolRef, "__nonzero__", getattr(BoolRef, "__bool__"))

    solver.push()
    for k, v in zip(init_keys, init_vals):
        solver.add(k == v)
    try:
        f()
    except:
        typ, value, tb = sys.exc_info()
        sys.excepthook(typ, value, tb.tb_next)
    solver.pop()

    delattr(BoolRef, "__bool__")
    delattr(BoolRef, "__nonzero__")

    # this path done
    if trace:
        solver.add(Not(And(*trace)))

    # choose a new path
    while trace:
        solver.push()
        solver.add(Not(trace[-1]))
        trace = trace[:-1]
        solver.add(*trace)
        r = solver.check()
        solver.pop()
        if r == sat:
            m = solver.model()
            new_init_vals = [m.eval(k, model_completion=True) for k in init_keys]
            cnt = mc_fuzz(f, init_keys, new_init_vals, cnt + 1)

    return cnt
