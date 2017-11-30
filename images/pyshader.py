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

class vec3():
  def __init__(s, x=0, y=None, z=None):
    s.x, s.y, s.z = (x, (x, y)[ y!=None ], (x, z)[ z!=None ])
  def mathop ( s, u, f ):
    return If_type(s, u, lambda: vec3(f(s.x, u.x), f(s.y, u.y), f(s.z, u.z)),
                         lambda: vec3(f(s.x, u),   f(s.y, u),  f(s.z, u)))
  __add__ = __radd__  = lambda s, u: s.mathop(u, op.add)
  __sub__ = __rsub__  = lambda s, u: s.mathop(u, op.sub)
  __mul__ = __rmul__  = lambda s, u: s.mathop(u, op.mul)
  __floordiv__ = __floordiv__  = lambda s, u: s.mathop(u, op.floordiv)
  __truediv__ = __truediv__  = lambda s, u: s.mathop(u, op.truediv)
  __str__ = lambda s: f"<{s.x}, {s.y}, {s.z}>"

def Apply_Vec(func, v, *args):
  if ( isinstance(v, vec3) ):
    return vec3(func(v.x, *args), func(v.y, *args), func(v.z, *args))
  if ( isinstance(v, vec2) ):
    return vec2(func(v.x, *args), func(v.y, *args))
  return func(v, *args)

def Apply_Vec2(func, v, u, *args):
  if ( isinstance(v, vec3) ):
    return vec3(func(v.x, u.x, *args), func(v.y, u.y, *args), func(v.z, u.z, *args))
  if ( isinstance(v, vec2) ):
    return vec2(func(v.x, u.x, *args), func(v.y, u.y, *args))
  return func(v, *args)

def Join_Vec(func, v):
  if ( isinstance(v, vec3) ): return func(v.x, func(v.y, v.z))
  if ( isinstance(v, vec2) ): return func(v.x, v.y)

length = lambda v: sqrt(Join_Vec(lambda u, v: u+v, Apply_Vec(sqr, v)))
mod    = lambda u, v: Apply_Vec2(lambda _u, _v: (_u%_v)-_v/2, u, v)
vmax   = lambda u, v: vec2(max(u.x, v.x), max(u.y, v.y));
vabs   = lambda u:    vec2(abs(u.x), abs(u.y))
dot    = lambda u, v: u.x*v.x + u.y*v.y

rot    = lambda uv, a: vec2(uv.x*cos(a) - uv.y*sin(a),
                            uv.y*cos(a) - uv.x*sin(a));

sqr = lambda u: Apply_Vec(lambda t:t*t, u);
def clamp ( u, a, b ):
  def _clamp(u, a, b):
    if ( u < a ): return a;
    if ( u > b ): return b;
    return u;
  return Apply_Vec(_clamp, u, a, b);

mix = lambda u, v, a: u*(1.0-a) + v*a

def Apply_Col ( col ):
  t = lambda a: clamp(int(a*255), 0, 255);
  return [t(col[0]), t(col[1]), t(col[2]), 255]
