from functools import *
import re
from aogenerics import *

def GenericMixin(overloads=None):
  " Gives many generic functions, overloads = string of operators to overload "
  overloads = ApplyL(lambda t: f"__{t}__", overloads.split(" ")) if (
                overloads != None ) else []
  class _GenericMixin(object):
    RLabels = lambda s: Zipget(s.__dict__.items(), 0)
    RValues = lambda s: s.RLabels().ApplyL(lambda x: getattr(s, x))

    def Component_apply(s, o, f):
      " Applies a function(S, O), S = s0..sn, O = o0..o[sn] "
      sl = s.RValues();
      ol = If_type(s, o, lambda:o.RValues(), lambda:[o for _t in range(0, o)])()
      reduct = lambda l: l.Reduce(lambda x, y: getattr(x, f)(y))
      return type(s)(*ApplyT(reduct, zip(sl, ol)))

    ROverloads = lambda: overloads

    if ( "__str__" in overloads ):
      __str__ = lambda s: str(s.RValues().Reduce(lambda x,y: f"{x}..{y}"))
      overloads.remove("__str__")

    if ( len(overloads) > 0 ):
      def ROverloads ( self ):
        return overloads

  " for function mixins (setattr), need to drop to function scope "
  for label in overloads:
    fcall = (label[:2]+label[3:]) if label[2] == "r" else label
    setattr(_GenericMixin, label,
            (lambda l: lambda s, o: s.Component_apply(o, l))(fcall))
  return _GenericMixin;
#}

class Interval(GenericMixin("radd rmul mul eq str")):
  def __init__(s, lo=0, hi=0): s.hi, s.lo = tuple(sorted([lo, hi]))
  def __add__(s, o):
    "Because [a,b]+[c,d] = [a-c, b+d], otherwise GenericMixin's add would work"
    i = If_type(s, o, lambda: o.RValues(), lambda: [-o, o])()
    return s.Component_apply(Interval(-i[0], i[1]), "__add__")

a  = Interval(2,3) # The interval from 2 ... 3
b  = Interval(4)   # the interval from 0 ... 4
c  = Interval()    # The interval 0 ... 0
aa = Interval(2,3) # Also the interval 2 ... 3
test = Interval(3,3) # Also the interval 2 ... 3

print("1Should be 2 ... 3 ",  a      )#1
print("2Should be 0 ... 4 ",  b      )#2
print("3Should be 0 ... 0 ",  c      )#3
print("4Should be 2...7 ",    a+b    )#4
print("5Should be -1...6 ",   a+test )#5
print("6Should be 1...6 ",   test+a  )#6
print("7Should be 10...14 ",  10+b   )#7
print("7Should be 10...14 ",  10+b   )#7
print("8Should be -10...-6 ", -10+b  )#8
print("9Should be 0...12 ",   a*b    )#9
print("10Should be 4...6 ",    a*2    )#0
#
#
print("should be true ",  a==a  ) # Needs __eq__( ) to work
print("should be false ", a==b  ) # Should be false
print("Should be true ",  a==aa ) # ditto
