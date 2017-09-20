"Many useful chaining and lazy-eval functions that operate on ranges"
from drange_primitives import *
from drange_interfaces import *
from drange           import *

# I need to figure out how to remove duplicate from here and drange...
class UFCS_Mixin(object):
  Map       = lambda s, fambda: Map(s, fambda)
  Take      = lambda s, amt: Take(s, amt)
  Filter    = lambda s, fambda: Filter(s, fambda).Array()
  Reduce    = lambda s, fambda, seed =None: Reduce(s, fambda, seed)
  Array     = lambda s: Array(s)
  Print_all = lambda s: Print_all(s)

class _BaseImpl(UFCS_Mixin):
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

class _EnumerateImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
    s.enumerator = 0
  Front = lambda s: (super().Front(), s.enumerator)
  def Pop_front(s):
    s.enumerator += 1
    super().Pop_front()
  Save = lambda s: Enumerate(s.drange)
  RStr = lambda s: "Enumerate"
def Enumerate(drange):
  # Lazily enumerates a range [supplies an index with pop_front: (elem, index)]
  assert Is_forward(drange)
  return _EnumerateImpl(drange.Save())

class _CycleImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
    s.cyclesave = drange.Save()
  Front = lambda s: super().Front()
  def Pop_front(s):
    super().Pop_front()
    if ( super().Empty() ):
      s.drange = s.cyclesave.Save()
  Save = lambda s: Cycle(s.drange)
  RStr = lambda s: "Cycle"
def Cycle(drange):
  # Lazily cycles a range [repeats range infinitely forward]
  assert Is_forward(drange)
  return _CycleImpl(drange.Save())

class _ZipImpl(_BaseImpl):
  def __init__(s, drange, orange):
    super().__init__(drange)
    s.orange = orange
  Front = lambda s: (super().Front(), s.orange.Front())
  def Pop_front(s):
    super().Pop_front()
    s.orange.Pop_front()
  def Empty(s):
    return s.orange.Empty() or s.drange.Empty()
  Save = lambda s: Zip(s.drange, s.orange)
  RStr = lambda s: "Zip"
def Zip(drange, orange):
  # Lazily zips a range
  assert Is_forward(drange)
  return _ZipImpl(drange.Save(), orange.Save())

class _StrideImpl(_BaseImpl):
  def __init__(s, drange, stridesize):
    super().__init__(drange)
    s.stridesize = stridesize
  def Pop_front(s):
    for i in range(0, s.stridesize):
      if ( not super().Empty() ):
        super().Pop_front()
  def Empty(s):
    e = s.drange.Save()
    for i in range(0, s.stridesize-1):
      if ( e.Empty() ):
        return True
      e.Pop_front()
    del e
    return False
  Save = lambda s: Stride(s.drange, s.stridesize)
  RStr = lambda s: "Stride"
def Stride(drange, stridesize):
  # Chunks a range by a chunk size
  assert Is_forward(drange)
  return _StrideImpl(drange.Save(), stridesize)

class _ChunksImpl(_BaseImpl):
  def __init__(s, drange, chunksize):
    super().__init__(drange)
    s.chunksize = chunksize
    s.befchunk = None
  def Front(s):
    if ( s.befchunk != None ):
      return s.befchunk
    s.befchunk = Range()
    for i in range(0, s.chunksize):
      if ( super().Empty() ):
        return s.befchunk
      s.befchunk += super().Front()
      super().Pop_front()
    return s.befchunk
  def Pop_front(s):
    s.befchunk = None
  Save = lambda s: Chunks(s.drange, s.chunksize)
  RStr = lambda s: "Chunks"
def Chunks(drange, chunksize):
  # Chunks a range by a chunk size
  assert Is_forward(drange)
  return _ChunksImpl(drange.Save(), chunksize)

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


##### non-lazy functions

def Chain(*dranges):
  # Chains ranges together in linear order
  orange = Range()
  for d in dranges:
    orange += d
  return orange

def Choose(lrange, rrange, lbool):
  return [lrange, rrange][lbool]

def Array(drange):
  """ Computes lazy range, returns Range of results """
  assert Is_forward(drange)
  g = drange.Save()
  from drange import Range
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

