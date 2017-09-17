"Many useful chaining and lazy-eval functions that operate on ranges"
from drange_primitives import *
from drange_interfaces import *
from drange           import *

class _BaseImpl():
  "Base implementation of functional class, with half-assed Invariants"
  def __init__(s, drange):
    s.drange = drange
  Invariant = lambda s: None
  def Empty(s):
    return s.drange.Empty()
  def Front(s):
    s.Invariant()
    return s.drange.Front()
  def Pop_front(s):
    s.Invariant()
    s.drange.Pop_front()
  RStr = lambda s: ""
  __str__ = lambda s: f"{s.RStr()} <{s.drange}>"

class _TakeImpl(_BaseImpl):
  def __init__(s, drange, amt):
    super().__init__(drange)
    s.drange = drange
    s.amt = amt
  Empty = lambda s: super().Empty() or s.amt == 0
  def Invariant(s):
    assert(s.amt > 0)
  def Pop_front(s): # can't use super().Pop_front()
    s.Invariant()
    s.amt -= 1
    s.drange.Pop_front()
  Save = lambda s: Take(s.drange, s.amt)
  RStr = lambda s: "Take"
def Take(drange, amt):
  " Takes a lazy amount from range, or the range length less than amount "
  assert Is_forward(drange)
  return _TakeImpl(drange.Save(), amt)

class _MapImpl(_BaseImpl):
  def __init__(s, drange, dlambda):
    super().__init__(drange)
    s.dlambda = dlambda
  Front = lambda s: s.dlambda(super().Front())
  Save = lambda s: Map(s.drange, s.dlambda)
  RStr = lambda s: "Map"
def Map(drange, dlambda):
  """ Lazily maps a lambda over a range, where each element in the returned
      range is the result of applying dlambda to it"""
  assert Is_forward(drange)
  return _MapImpl(drange.Save(), dlambda)

class _FilterImpl(_BaseImpl):
  def __init__(s, drange, dlambda):
    super().__init__(drange)
    s.dlambda = dlambda
  Front = lambda s: super().Front() if s.dlambda(super().Front()) else None
  Save = lambda s: Filter(s.drange, s.dlambda)
  RStr = lambda s: "Filter"
def Filter(drange, dlambda):
  """ Lazily filters the range, where each element in the returned range
      returned true when applied to dlambda """
  assert Is_forward(drange) and not drange.Empty()
  return _FilterImpl(drange.Save(), dlambda)


class _ReduceImpl(_BaseImpl):
  def __init__(s, drange, dlambda, seed):
    super().__init__(drange)
    (s.dlambda, s.has_front, s.seed) = (dlambda, 0, seed)
  def Front(s):
    if ( not s.has_front ):
      s.has_front = 1
      s.seed = s.dlambda(s.seed, super().Front())
    return s.seed
  def Pop_front(s):
    s.has_front = 0
    super().Pop_front()
  Save = lambda s: Reduce_range(s.drange, s.dlambda, s.seed)
  RStr = lambda s: "Reduce"
def Reduce_range(drange, dlambda, seed=None):
  "Reduces a drange with a dlambda (x, y) returning the resulting lazy range"
  assert Is_forward(drange) and not drange.Empty()
  # pop seed
  copy = drange.Save()
  reduce_seed = copy.Front() if seed is None else seed
  if ( seed is None ):
    assert(not copy.Empty())
    copy.Pop_front()
  return _ReduceImpl(copy, dlambda, reduce_seed)

def Reduce(drange, dlambda, seed=None):
  """Reduces a drange nonlazily with a dlambda (x, y), returns the result as a
       single value, and not the resulting reduce range"""
  drange = Array(Reduce_range(drange, dlambda, seed))
  assert ( not drange.Empty() )
  return drange[-1]


#####

def Array(drange):
  """ Computes lazy range, returns Range of results """
  assert Is_forward(drange)
  g = drange.Save()
  orange = Range()
  while ( not g.Empty() ):
    front = g.Front()
    if ( front != None ):
      orange.Put(front)
    g.Pop_front()
  return orange

def Iota(begin, end, stride=1):
  " A range from begin to end, with optional stride "
  orange = Range()
  while ( begin < end ):
    orange.Put(begin)
    begin += stride
  return orange

def Print_all(drange, recurse=0):
  """ Deep print of all of range elements """
  assert Is_forward(drange)
  drange = drange.Save()
  if ( recurse == 0 ):
    print("------------------------------------")
  print(" "*recurse, drange.__str__())
  while ( not drange.Empty() ):
    front = drange.Front()
    drange.Pop_front()
    if ( Is_forward(front) ):
      Print_all(front, recurse+2)
    else:
      print(" "*recurse + front.__str__())
  if ( recurse == 0 ):
    print("------------------------------------")
