from scipy import misc
from functools import *
from math import *
import numpy as np
import matplotlib.pyplot as plt
import operator as op

def If_type ( l, r, itrue, ifalse ):
  return (ifalse, itrue)[isinstance(l, type(r))]()


class vec2():
  def __init__(s, x=0, y=None):
    s.x, s.y = (x, (x, y)[ y!=None ])
  def mathop ( s, u, f ):
    return If_type(s, u, lambda: vec2(f(s.x, u.x), f(s.y, u.y)),
                         lambda: vec2(f(s.x, u),   f(s.y, u)))
  __add__ = __radd__  = lambda s, u: s.mathop(u, op.add)
  __sub__ = __rsub__  = lambda s, u: s.mathop(u, op.sub)
  __mul__ = __rmul__  = lambda s, u: s.mathop(u, op.mul)
  __floordiv__ = __floordiv__  = lambda s, u: s.mathop(u, op.floordiv)
  __truediv__ = __truediv__  = lambda s, u: s.mathop(u, op.truediv)
  __str__ = lambda s: f"<{s.x}, {s.y}>"

length = lambda v: sqrt(v.x*v.x + v.y*v.y);
rot    = lambda uv, a: vec2(uv.x*cos(a) - uv.y*sin(a),
                            uv.y*cos(a) - uv.x*sin(a));
mod    = lambda u, v: vec2((u.x % v.x) - v.x/2,
                           (u.y % v.y) - v.y/2);
vmax   = lambda u, v: vec2(max(u.x, v.x), max(u.y, v.y));
vabs   = lambda u:    vec2(abs(u.x), abs(u.y))
dot    = lambda u, v: u.x*v.x + u.y*v.y
