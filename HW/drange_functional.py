"Many useful chaining and lazy-eval functions that operate on ranges"
from drange_primitives import *
from drange_interfaces import *
from drange           import *

# I need to figure out how to remove duplicate from here and drange...
class UFCS_Mixin(object):
  UFCS_Save = lambda s: Try_save(s)
  Array     = lambda s               : Array(s.UFCS_Save())
  Chain     = lambda s, *args        : Chain(s.UFCS_Save(), *args)
  Chunks    = lambda s, chunksize    : Chunks(s.UFCS_Save(), chunksize)
  Cycle     = lambda s               : Cycle(s.UFCS_Save())
  Each      = lambda s, f            : Each(s.UFCS_Save(), f)
  Enumerate = lambda s               : Enumerate(s.UFCS_Save())
  Filter    = lambda s, f            : Filter(s.UFCS_Save(), f)
  Join      = lambda s, f            : Join(s.UFCS_Save(), f)
  Map       = lambda s, f            : Map(s.UFCS_Save(), f)
  Print_all = lambda s               : Print_all(s.UFCS_Save())
  Reduce    = lambda s, f, seed=None : Reduce(s.UFCS_Save(), f, seed)
  Retro     = lambda s               : Retro(s.UFCS_Save())
  Split     = lambda s, f            : Split(s.UFCS_Save(), f)
  Stride    = lambda s, strideamt    : Stride(s.UFCS_Save(), strideamt)
  Take      = lambda s, amt          : Take(s.UFCS_Save(), amt)
  Tee       = lambda s, f            : Tee(s.UFCS_Save(), f)
  Zip       = lambda s, o            : Zip(s.UFCS_Save(), o)
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

# --------------------------------------------------------------------------- #
#  lazy functions

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
  Save = lambda s: Take(Try_save(s.drange), s.amt)
  RStr = lambda s: "Take"
def Take(drange, amt):
  " Takes a lazy amount from range, or the range length less than amount "
  assert Is_input(drange)
  return _TakeImpl(drange, amt)

class _JoinImpl(_BaseImpl):
  def __init__(s, drange, dlambda):
    from drange import Range
    super().__init__(drange)
    s.dlambda = dlambda;
  def Front(s):
    from drange import Range
    s.drt = Range()
    while True:
      if ( s.drange.Empty() ): break;
      t = s.drange.Front()
      if ( s.dlambda(t) ): break;
      s.drt += t
    return s.drt;
  Empty = lambda s: s.drange.Empty()
  Save = lambda s: Join(Try_save(s.drange), s.dlambda)
  RStr = lambda s: "Join"
def Join(drange, dlambda):
  """ Joins a range into multiple ranges using dlambda """
  assert Is_input(drange)
  return _JoinImpl(drange, dlambda)


class _MapImpl(_BaseImpl):
  def __init__(s, drange, dlambda):
    super().__init__(drange)
    s.dlambda = dlambda
  Front = lambda s: s.dlambda(s.drange.Front())
  Save = lambda s: Map(Try_save(s.drange), s.dlambda)
  RStr = lambda s: "Map"
def Map(drange, dlambda):
  """ Lazily maps a lambda over a range, where each element in the returned
      range is the result of applying dlambda to it"""
  assert Is_input(drange)
  return _MapImpl(drange, dlambda)

class _TeeImpl(_BaseImpl):
  def __init__(s, drange, dlambda):
    super().__init__(drange)
    s.dlambda = dlambda
  def Front(s):
    val = s.drange.Front()
    s.dlambda(val)
    return val
  Save = lambda s: Tee(Try_save(s.drange), s.dlambda)
  RStr = lambda s: "Tee"
def Tee(drange, dlambda):
  """ Lazily tees a lambda over a range, which applies dlambda to each element
      but returns the original range (for side effects in middle of a chain,
      ei, print) """
  assert Is_input(drange)
  return _TeeImpl(drange, dlambda)

class _RetroImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
  Front = lambda s: s.drange.Back()
  Save = lambda s: Retro(Try_save(s.drange))
  RStr = lambda s: "Retro"
def Retro(drange):
  # Iterates a bidirectional range backwards
  assert Is_bidirectional(drange)
  return _RetroImpl(drange)

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
  Save = lambda s: Filter(Try_save(s.drange), s.dlambda, s.uppity)
  RStr = lambda s: "Filter"
def Filter(drange, dlambda, seed=None):
  """ Lazily filters the range, where each element in the returned range
      returned true when applied to dlambda """
  return _FilterImpl(drange, dlambda, seed)

class _EnumerateImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
    s.enumerator = 0
  def Front(s):
    val = (s.drange.Front(), s.enumerator+1)
    s.enumerator += 1
    print("VAL: ", val)
    return val
  Save = lambda s: Enumerate(Try_save(s.drange))
  RStr = lambda s: "Enumerate"
def Enumerate(drange):
  # Lazily enumerates a range [supplies an index with: (elem, index)]
  assert Is_input(drange)
  return _EnumerateImpl(drange)

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
  Save = lambda s: Cycle(Try_save(s.drange))
  RStr = lambda s: "Cycle"
def Cycle(drange):
  # Lazily cycles a forward range [repeats range infinitely forward]
  assert Is_forward(drange)
  return _CycleImpl(drange)

class _ZipImpl(_BaseImpl):
  def __init__(s, drange, orange):
    super().__init__(drange)
    s.orange = orange
  Front = lambda s: (s.drange.Front(), s.orange.Front())
  Empty = lambda s: s.orange.Empty() or s.drange.Empty()
  Save = lambda s: Zip(Try_save(s.drange), Try_save(s.orange))
  RStr = lambda s: "Zip"
def Zip(drange, orange):
  # Lazily zips a range
  assert Is_input(drange) and Is_input(orange)
  return _ZipImpl(drange, orange)

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
  Save = lambda s: Stride(Try_save(s.drange), s.stridesize)
  RStr = lambda s: "Stride"
def Stride(drange, stridesize):
  # Chunks a range by a chunk size
  assert Is_input(drange)
  return _StrideImpl(drange, stridesize)

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
  Save = lambda s: Chunks(Try_save(s.drange), s.chunksize)
  RStr = lambda s: "Chunks"
def Chunks(drange, chunksize):
  # Chunks a range by a chunk size
  assert Is_input(drange)
  return _ChunksImpl(drange, chunksize)

class _ChainImpl(_BaseImpl):
  def __init__(s, drange):
    super().__init__(drange)
    s.front = None
    s.Refresh_front()
  def Front_empty(s):
    return s.front == None or s.front.Empty()
  def Refresh_front(s):
    # iterate through until a non-empty chain or chain is empty
    while ( s.Front_empty() ):
      if ( s.drange.Empty() ): return
      s.front = s.drange.Front()
  def Front(s):
    rval = s.front.Front()
    s.Refresh_front()
    return rval
  Empty = Front_empty
  def Save(s):
    from drange import Range
    return _ChainImpl(Try_save(Range(s.front) + s.drange))
  RStr = lambda s: "Chain"
def Chain(*oranges):
  # Chain a range by multiple ranges lazily
  from drange import Range
  orange = Range()
  for i in oranges:
    assert(Is_input(i))
    orange += Range(Try_save(i))
  return _ChainImpl(orange)

class _IotaImpl(_BaseImpl):
  def __init__(s, start, end, stride):
    super().__init__(f"{start} -> {end} by {stride}") # for string
    (s.it, s.end, s.stride) = (start, end, stride)
  Empty = lambda s: s.it >= s.end
  def Front(s):
    assert(not s.Empty())
    s.it += s.stride
    return s.it - s.stride
  Save = lambda s: Iota(s.it, s.end, s.stride)
  RStr = lambda s: "Iota"
def Iota(start=0, end=10, stride=1):
  " Iotas a lazy amount from range, or the range length less than amount "
  return _IotaImpl(start, end, stride)

class _GenerateImpl(_BaseImpl):
  def __init__(s, fambda):
    super().__init__(f"")
    s.fambda = fambda
  Empty = InfiniteEmpty()
  def Front(s):
    return s.fambda()
  Save = lambda s: Generate(s.fambda)
  RStr = lambda s: "Generate"
def Generate(fambda):
  " Generates a range whose front is defined by calls of fambda "
  return _GenerateImpl(fambda)

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
  Save = lambda s: Split(Try_save(s.drange), s.fambda)
  RStr = lambda s: "Split"
def Split(drange, fambda):
  # Split a range by a chunk size
  assert Is_input(drange)
  return _SplitImpl(drange, fambda)

class _ReduceImpl(_BaseImpl):
  def __init__(s, drange, dlambda, seed):
    super().__init__(drange)
    (s.dlambda, s.has_front, s.seed) = (dlambda, 0, seed)
  def Front(s):
    s.seed = s.dlambda(s.seed, s.drange.Front())
    return s.seed
  Save = lambda s: Reduce_range(Try_save(s.drange), s.dlambda, s.seed)
  RStr = lambda s: "Reduce"
def Reduce_range(drange, dlambda, seed=None):
  "Reduces a drange with a dlambda (x, y) returning the resulting lazy range"
  assert Is_input(drange)
  if ( drange.Empty() ):
    return seed
  # pop seed
  reduce_seed = drange.Front() if seed is None else seed
  return _ReduceImpl(drange, dlambda, reduce_seed)

def Reduce(drange, dlambda, seed=None):
  """Reduces a drange nonlazily with a dlambda (x, y), returns the result as a
       single value, and not the resulting reduce range"""
  drange = Array(Reduce_range(drange, dlambda, seed))
  assert ( not drange.Empty() )
  return drange[-1]

# --------------------------------------------------------------------------- #
#  non lazy functions

def Choose(lrange, rrange, lbool):
  return [lrange, rrange][lbool]

def Array(drange):
  """ Computes lazy range, returns Range of results """
  from drange import Range
  assert Is_input(drange)
  g = Try_save(drange)
  orange = Range()
  while ( not g.Empty() ):
    front = g.Front()
    if ( front != None ):
      orange.Put(front)
  return orange

def PArray(drange):
  """ Computes lazy range, returns python array of results """
  from drange import Range
  assert Is_input(drange)
  g = Try_save(drange)
  orange = []
  while ( not g.Empty() ):
    front = g.frint()
    if ( front != None ):
      orange += [front];
  return orange;

def Each(drange, fambda):
  """ Applies fambda to each element of drange, non-lazily (equivalent to
      range.Tee(fambda).Array() """
  drange.Tee(fambda).Array()

def Print_all(drange, recurse=0):
  """ Deep print of all of range elements """
  assert Is_input(drange)
  drange = Try_save(drange)
  if ( recurse == 0 ):
    print("------------------------------------")
  print(" "*(recurse-1), drange.__str__())
  while ( not drange.Empty() ):
    front = drange.Front()
    if ( Is_input(front) ):
      Print_all(front, recurse+2)
    else:
      print(" "*(recurse+1) + front.__str__())
  if ( recurse == 0 ):
    print("------------------------------------")

