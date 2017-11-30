"""This module contains many utilities for working with custom ranges, such as
   static introspection, along with convenience functions for manipulating
   ranges"""
from drange_interfaces import *

def Is_input(drange):
  return (hasattr(drange, "Empty") and hasattr(drange, "Front"))

def Is_output(drange):
  return hasattr(drange, "Put")

def Is_forward(drange):
  return (Is_input(drange) and hasattr(drange, "Save"))

def Is_forward_output(drange):
  return Is_forward(drange) and Is_output(drange)

def Is_bidirectional(drange):
  return (Is_forward(drange) and hasattr(drange, "Back"))

def Is_bidirectional_output(drange):
  return (Is_bidirectional(drange) and Is_output(drange) and
          hasattr(drange, "Put_back"))

def Is_random_access(drange):
  return (Is_bidirectional(drange) and hasattr(drange, "__getitem__"))

def Is_random_access_output(drange):
  return Is_random_access(drange) and Is_bidirection_output(drange)

def Is_random_access_assignable(drange):
  return Is_random_access_output(drange) and hasattr(drange, "__setitem__")

class InfiniteEmpty():
  """ A hack to allow infinite ranges so users don't have to check
      (ifisinstance(s.Empty, int)) and Is_infinite introspection can work
      despite Empty always returning false.
  """
  __call__ = lambda s: False

def Is_infinite(drange):
  return hasattr(drange, "Empty") and isinstance(drange.Empty, InfiniteEmpty)


def Pop_front_n(drange, n, dlambda=None):
  assert(Is_input(drange))
  """Advances a range up to n elements, returns the number of iterations
     left if the range empties before n advances"""
  while ( not drange.Empty() and n != 0 ):
    n -= 1
    a = drange.Front()
    if ( dlambda != None ): dlambda(a)
  return n

def Pop_back_n(drange, n, dlambda=None):
  """Advances a bidirectional range up to n elements from the back, returns the
     number of iterations left if the range empties before n advances"""
  assert(Is_bidirectional(drange))
  while ( not drange.Empty() and n != 0 ):
    n -= 1
    a = drange.Back()
    if ( dlambda != None ): dlambda(a)
  return n

def Move_front(drange, dlambda=None):
  "Removes and returns the front element of a range"
  assert(Is_input(drange))
  assert(not drange.Empty())
  t = drange.Front()
  return (t if dlambda==None else dlambda(t))

def Move_back(drange, dlambda=None):
  "Removes and returns the back element of a bidirectional range"
  assert(Is_bidirectional(drange))
  assert(not drange.Empty())
  t = drange.Back()
  return (t if dlambda==None else dlambda(t))

def Move_at(drange, i, dlambda=None):
  """Removes and returns the i'th element of a random-access range,
      NOTE: this only works with ranges that delete on setitem(None)!"""
  if ( Is_random_access(drange) ):
    t = drange.__getitem__(i)
    drange.__setitem__(i, None)
    return t
  # last index
  if ( i == -1 ):
    t = drange.Front();
    while ( not drange.Empty() ):
      t = drange.Front();
    return t;

  amt = 0;
  while ( not drange.Empty() and amt < i-1 ):
    amt += 1
    drange.Front()
  return drange.Front()

def Walk_length(drange):
  """Walks the length of a forward range, computing at O(n) time"""
  assert(Is_forward(drange))
  drange = drange.Save()
  amt = 0
  while ( not drange.Empty() ):
    amt += 1
    drange.Front()
  return amt

def StrRange(_str):
  from drange import Range
  return Range(*list(_str))

def PyRange(_drange):
  assert(Is_forward(_drange))
  drange = _drange.Save()
  ts = []
  while ( not drange.Empty() ):
    ts += [drange.Front()]
  return ts

def PyIter(_drange):
  class _TempDrangeIterator:
    def __init__(s, drange):
      s.drange = drange.Save()
    __iter__ = lambda s: s
    def __next__(s):
      if ( s.drange.Empty() ):
        raise StopIteration
      return s.drange.Front()
  return _TempDrangeIterator(_drange)

def Try_save(drange):
  if ( Is_forward(drange) ):
    return drange.Save()
  return drange
