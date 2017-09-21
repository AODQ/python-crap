"Many useful chaining and lazy-eval functions that operate on ranges"
from drange_primitives import *
from drange_interfaces import *
from drange           import *

# I need to figure out how to remove duplicate from here and drange...
class UFCS_Mixin(object):
  Map       = lambda s, fambda             : Map(s, fambda)
  Take      = lambda s, amt                : Take(s, amt)
  Filter    = lambda s, fambda             : Filter(s, fambda)
  Reduce    = lambda s, fambda, seed =None : Reduce(s, fambda, seed)
  Retro     = lambda s                     : Retro(s)
  Array     = lambda s                     : Array(s)
  Print_all = lambda s                     : Print_all(s)
  Split     = lambda s, fambda             : Split(s, fambda)
  Chain     = lambda s, *args              : Chain(s, *args)
  Stride    = lambda s, strideamt          : Stride(s, strideamt)
  Enumerate = lambda s                     : Enumerate(s)
  Cycle     = lambda s                     : Cycle(s)
  Chunks    = lambda s, chunksize          : Chunks(s, chunksize)
  Zip       = lambda s, o                  : Zip(s, o)
  Tee       = lambda s, fambda             : Tee(s, fambda)
  def Drop(s, n):
    trange = s.Save()
    Pop_front_n(trange, n)
    return trange
  def Dropback(s, n):
    trange = s.Save()
    Pop_back_n(trange, n)
    return trange
  def __iter__(s):
    from drange_primitives import PyIter
    return PyIter(s)

class _BaseImpl(UFCS_Mixin):
  "Base implementation of functional class, with half-assed Invariants"
  def __init__(s, drange):
    s.drange = drange
  RStr = lambda s: ""
  Front = lambda s: s.drange.Front()
  Empty = lambda s: s.drange.Empty()
  __str__ = lambda s: f"{s.RStr()} <{s.drange}>"

class _TakeImpl(_BaseImpl):
  def __init__(s, drange, amt):
    super().__init__(drange)
    s.drange = drange
    s.amt = amt
  Empty = lambda s: s.drange.Empty() or s.amt == 0
  def Front(s):
    assert(s.amt > 0)
    s.amt -= 1
    return s.drange.Front()
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
  Front = lambda s: s.dlambda(s.drange.Front())
  Save = lambda s: Map(s.drange, s.dlambda)
  RStr = lambda s: "Map"
def Map(drange, dlambda):
  """ Lazily maps a lambda over a range, where each element in the returned
      range is the result of applying dlambda to it"""
  assert Is_forward(drange)
  return _MapImpl(drange.Save(), dlambda)

class _TeeImpl(_BaseImpl):
  def __init__(s, drange, dlambda):
    super().__init__(drange)
    s.dlambda = dlambda
  def Front(s):
    val = s.drange.Front()
    s.dlambda(val)
    return val
  Save = lambda s: Tee(s.drange, s.dlambda)
  RStr = lambda s: "Tee"
def Tee(drange, dlambda):
  """ Lazily tees a lambda over a range, which applies dlambda to each element
      but returns the original range (for side effects in middle of a chain,
      ei, print) """
  assert Is_forward(drange)
  return _TeeImpl(drange.Save(), dlambda)

class _RetroImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
  Front = lambda s: s.drange.Back()
  Save = lambda s: Retro(s.drange)
  RStr = lambda s: "Retro"
def Retro(drange):
  # Iterates a bidirectional range backwards
  assert Is_bidirectional(drange)
  return _RetroImpl(drange.Save())

class _FilterImpl(_BaseImpl):
  def __init__(s, drange, dlambda, seed=None):
    super().__init__(drange)
    s.dlambda = dlambda
    s.uppity = seed
    if ( seed == None ): s.Front()
  def Front(s):
    val = s.uppity
    while ( not s.drange.Empty() ):
      front = s.drange.Front()
      if ( s.dlambda(front) ):
        s.uppity = front
        return val
    s.uppity = None
    return val
  Empty = lambda s: s.uppity == None
  Save = lambda s: Filter(s.drange, s.dlambda, s.uppity)
  RStr = lambda s: "Filter"
def Filter(drange, dlambda, seed=None):
  """ Lazily filters the range, where each element in the returned range
      returned true when applied to dlambda """
  assert Is_forward(drange) and not drange.Empty()
  return _FilterImpl(drange.Save(), dlambda, seed)

class _EnumerateImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
    s.enumerator = 0
  def Front(s):
    val = (s.drange.Front(), s.enumerator)
    s.enumerator += 1
    return val
  Save = lambda s: Enumerate(s.drange)
  RStr = lambda s: "Enumerate"
def Enumerate(drange):
  # Lazily enumerates a range [supplies an index with: (elem, index)]
  assert Is_forward(drange)
  return _EnumerateImpl(drange.Save())

class _CycleImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
    s.cyclesave = drange.Save()
  Empty = InfiniteEmpty()
  def Front(s):
    val = s.drange.Front()
    if ( s.drange.Empty() ):
      s.drange = s.cyclesave.Save()
    return val
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
  Front = lambda s: (s.drange.Front(), s.orange.Front())
  Empty = lambda s: s.orange.Empty() or s.drange.Empty()
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
  def Front(s):
    v = s.drange.Front()
    for i in range(1, s.stridesize):
      if ( s.drange.Empty() ): break
      s.drange.Front()
    return v
  def Empty(s): return s.drange.Empty()
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
  def Front(s):
    from drange import Range
    bchunk = Range()
    for i in range(0, s.chunksize):
      if ( s.drange.Empty() ):
        return bchunk
      bchunk += s.drange.Front()
    return bchunk
  Save = lambda s: Chunks(s.drange, s.chunksize)
  RStr = lambda s: "Chunks"
def Chunks(drange, chunksize):
  # Chunks a range by a chunk size
  assert Is_forward(drange)
  return _ChunksImpl(drange.Save(), chunksize)

class _SplitImpl(_BaseImpl):
  def __init__(s, drange, fambda):
    super().__init__(drange)
    s.fambda = fambda
  def Front(s):
    from drange import Range
    bchunk = Range()
    while not s.drange.Empty():
      val = s.drange.Front()
      if ( s.fambda(val) ):
        break;
      bchunk += val
    return bchunk
  Save = lambda s: Split(s.drange, s.fambda)
  RStr = lambda s: "Split"
def Split(drange, fambda):
  # Split a range by a chunk size
  assert Is_forward(drange)
  return _SplitImpl(drange.Save(), fambda)

class _ReduceImpl(_BaseImpl):
  def __init__(s, drange, dlambda, seed):
    super().__init__(drange)
    (s.dlambda, s.has_front, s.seed) = (dlambda, 0, seed)
  def Front(s):
    s.seed = s.dlambda(s.seed, s.drange.Front())
    return s.seed
  Save = lambda s: Reduce_range(s.drange, s.dlambda, s.seed)
  RStr = lambda s: "Reduce"
def Reduce_range(drange, dlambda, seed=None):
  "Reduces a drange with a dlambda (x, y) returning the resulting lazy range"
  assert Is_forward(drange) and not drange.Empty()
  # pop seed
  copy = drange.Save()
  reduce_seed = copy.Front() if seed is None else seed
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
  from drange import Range
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
  return orange

def Iota(begin, end, stride=1):
  " A range from begin to end, with optional stride "
  from drange import Range
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
    if ( Is_forward(front) ):
      Print_all(front, recurse+2)
    else:
      print(" "*recurse + front.__str__())
  if ( recurse == 0 ):
    print("------------------------------------")

