"""
DLang inspired Range implementation in python. Advantages over lists:
  Static Typing with 'Any' and Variant option
  Memory pool [Slices do not copy unless modified] X
  Many different range types:
    Input, Forward, Bidirectional, Random Access X
    Output, Assignable, Infinite                 X
  Introspection functions (Is_input, Is_infinte, etc) X
  "UFCS"-optional chaining functions:
    map, filter, reduce, chain, enumerate, drop, dropback, cycle, iota, chunks,
    choose, zip, stride, tee, take, array, and retro
  To change size, just write to a range's length X
Other things:
  + to concatenate, == for equality. X
Restrictions:
  python lists, maps, dicts, etc are not allowed in a range
"""

class __MemoryPool:
  """
  A range slice is only a new view on memory, it does not create a new copy,
  however if a modification is made to the memory pool where multiple viewers
  exist, a copy will be made. The memory is freed using refcounts
  """
  def __init__(s):
    s._mempool = {} #{ID : [refcount, memory]}
    s._freemem = []
    s._counter = 0
  def Report_leaked_memory(s):
    pass
  def RSlice_count(s):
    return len(s._mempool)
  def Allocate(s, memory):
    # Allocate a chunk of memory, returns the 'ptr'
    if ( len(s._freemem) > 0 ):
      (ptr, s._freemem) = (s._freemem[0], s._freemem[1:])
    else:
      s._counter += 1
      ptr = s._counter
    s._mempool[ptr] = [1, list(memory)]
    return ptr
  def Deallocate(s, ptr):
    assert ( ptr in s._mempool )
    s._mempool[ptr][0] -= 1
    if ( s._mempool[ptr][0] <= 0 ):
      s._freemem += [ptr]
      del s._mempool[ptr]
  def Slice(s, ptr):
    s._mempool[ptr][0] += 1
  def Touch(s, ptr, dealloc=0):
    if ( s._mempool[ptr][0] == 1 ): return ptr
    tptr = s.Allocate(s._mempool[ptr][1])
    s.Deallocate(ptr)
    return tptr
  def PushElement(s, ptr, element):
    """ USAGE: ptr = Selement """
    ptr = s.Touch(ptr, dealloc=1)
    s._mempool[ptr][1] += [element]
    return ptr
  def SElement(s, ptr, index, element):
    """ USAGE: ptr = Selement """
    ptr = s.Touch(ptr, dealloc=1)
    s._mempool[ptr][1][index] = element
    return ptr
  def RElement(s, ptr, index):
    return s._mempool[ptr][1][index]

_memorypool = __MemoryPool()

class Any:
  pass

class Variant:
  """ Variant using built-in python list """
  def __init__(s, *args):
    s._types = args
  def Superset(s, o):
    """ Returns true if s is a superset of o """
    amt = 0
    g = len(o)
    while ( g != 0 ):
      amt += (g in s)
    print(amt)

class TemplateRange:
  """ A template range that works with memory pool.
        Usage: Any|ForwardRange(10, "hi", int|ForwardRange(10, 20))
  """
  def __init__(s, *args, noalloc=None):
    s._type = Any
    (s.begin, s.end) = (0, len(args))
    if ( not noalloc ):
      s._ptr = _memorypool.Allocate(args)
  def __del__(s):
    _memorypool.Deallocate(s._ptr)
  def __ror__(s, type):
    """ Type check """
    s._type = type if isinstance(type, Variant) else Variant(type)
    # verify type TODO
    return s
  def Compatible(s, o):
    "Returns if the type of s is a superset of o [for say, s+o]"
    if ( s._type == Any ): return true
    else if ( o._type == Any ): return false
    return s.Variant(o)

class _FakeFront():
  """To allow: myrange.Front() , or myrange.Front.Set(5)"""
  def __init__(s, trange):
    s._trange = trange
  def Invariant(s):
    assert s._trange.begin < s._trange.end
  def __call__(s):
    s.Invariant()
    return _memorypool.RElement(s._trange._ptr, s._trange.begin)
  def Set(s, o):
    s.Invariant()
    s._trange._ptr = _memorypool.SElement(s._trange._ptr, s._trange.begin, o)
  def Apply(s, fambda):
    s.Invariant()
    s.Set(fambda(_memorypool.RElement(s._trange._ptr, s._trange.begin)))

class InputRange(TemplateRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
    s.Front = _FakeFront(s)
  def Empty(s):
    return s.begin == s.end
  def Pop_front(s):
    assert s.begin < s.end
    s.begin += 1
  def __str__(s):
    return f"<InputRange {s._type}>"

class ForwardRange(InputRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  def Save(s):
    sav = (type(s))(noalloc=True)
    sav._type = s._type
    (sav.begin, sav.end) = (s.begin, s.end)
    sav._ptr = s._ptr
    _memorypool.Slice(sav._ptr)
    return sav
  def __eq__(s, o):
    savs = s.Save()
    savo = o.Save()
    while ( not savs.Empty() and not savo.Empty() ):
      if ( savs.Front() != savo.Front() ):
        return False
      savs.Pop_front()
      savo.Pop_front()
    return savs.Empty() and savo.Empty()

class BidirectionalRange(ForwardRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  # def Back(s):
  #   assert s.end-1 > s.begin
  #   return _memorypool[s._ptr][s.end-1]
  # def Pop_back(s):
  #   assert s.end-1 > s.begin
  #   s.end -= 1

class RandomAccessRange(BidirectionalRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  def __getitem__(s, key):
    if ( isinstance(key, slice) ):
      dslice = (type(s))(noalloc=True)
      _memorypool.Slice(s._ptr)
      dslice._type = s._type
      dslice._ptr = s._ptr
      start, end, step = key.indices(s.end - s.begin)
      (dslice.begin, dslice.end) = (s.begin + start, s.begin + end)
      return dslice
    return _memorypool.RElement(s._ptr, key)
  def __setitem__(s, index, value):
    s._ptr = _memorypool.SElement(s._ptr, index, value)

class OutputRange(TemplateRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  def Put(s, element):
    s._ptr = _memorypool.PushElement(s._ptr, element)
    s.end += 1

class Range(RandomAccessRange, OutputRange):
  """ The 'array' implementation of range; giving power of ranges with
      convenience utility functions
  """
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)

  def Length(s, length=-1):
    if ( length >= 0 ):
      assert(length <= s.Length())
      s.end = s.begin + length
      # TODO touch memory pool
    return s.end-s.begin

  def __add__(s, o):
    assert(Is_input(o))
    assert(s.Compatible(o))
    (dfrom, dto) = (o.Save(), s.Save())
    while ( not dfrom.Empty() ):
      dto.Put(dfrom.Front())
      dfrom.Pop_front()
    return dto

def _RFuncRange(drange):
  """Saves the range if applicable"""
  return drange.Save() if isinstance(drange, ForwardRange) else drange

def Is_input(drange):
  return (hasattr(drange, "Empty") and
          hasattr(drange, "Pop_front") and
          hasattr(drange, "Front"))

def Is_output(drange):
  return hasattr(drange, "Put")

def Is_forward(drange):
  return (Is_input(drange) and hasattr(drange, "Save"))

def Is_forward_output(drange):
  return Is_forward(drange) and Is_output(drange)

def Is_bidirectional(drange):
  return (Is_forward(drange) and hasattr(drange, "Back") and
                                 hasattr(drange, "Pop_back"))

def Is_bidirectional_output(drange):
  return (Is_bidirectional(drange) and Is_output(drange) and
          hasattr(drange, "Put_back"))

def Is_random_access(drange):
  return (Is_bidirectional(drange) and hasattr(drange, "__getitem__"))

def Is_random_access_output(drange):
  return Is_random_access(drange) and Is_bidirection_output(drange)

def Is_random_access_assignable(drange):
  return Is_random_access_output(drange) and hasattr(drange, "__setitem__")

def Take(drange, amt):
  """ Takes amt from range (lazily), otherwise the range length if the amt is
      less than it """
  assert Is_forward(drange)
  class _Take:
    def __init__(s, drange, amt):
      s.drange = drange
      s.amt = amt
    def Empty(s):
      return (s.drange.Empty() or s.amt == 0)
    # Empty = lambda s: (s.drange.Empty() or s.amt == 0)
    def Front(s):
      assert(s.amt > 0)
      return s.drange.Front()
    def Pop_front(s):
      assert(s.amt > 0)
      s.amt -= 1
      s.drange.Pop_front()
    def Save(s):
      return Take(s.drange, s.amt)
    def __str__(s):
      return f"<Take {s.drange}>"
  return _Take(drange.Save(), amt)

def Map(drange, dlambda):
  assert Is_forward(drange)
  class _Map:
    def __init__(s, drange, dlambda):
      s.drange = drange
      s.dlambda = dlambda
    def Empty(s):
      return s.drange.Empty()
    def Front(s):
      return dlambda(s.drange.Front())
    def Pop_front(s):
      s.drange.Pop_front()
      s.has_front = 0
    def Save(s):
      return Map(s.drange, s.dlambda)
    def __str__(s):
      return f"<Map {s.drange}>"
  return _Map(drange.Save(), dlambda)

def Filter(drange, dlambda):
  assert Is_forward(drange) and not drange.Empty()
  class _Filter:
    def __init__(s, drange, dlambda):
      s.drange = drange
      s.dlambda = dlambda
    def Empty(s):
      return s.drange.Empty()
    def Front(s):
      return s.drange.Front() if dlambda(s.drange.Front()) else None
    def Pop_front(s):
      s.drange.Pop_front()
    def Save(s):
      return Filter(s.drange, s.dlambda)
    def __str__(s):
      return f"<Reduce {s.drange}>"
  return _Filter(drange.Save(), dlambda)

def ReduceImpl(drange, dlambda, seed=None):
  assert Is_forward(drange) and not drange.Empty()
  # pop seed
  copy = drange.Save()
  reduce_seed = copy.Front() if seed is None else seed
  if ( seed is None ):
    assert(not copy.Empty())
    copy.Pop_front()

  class _Reduce:
    def __init__(s, drange, dlambda, seed):
      s.drange = drange
      s.dlambda = dlambda
      s.has_front = 0
      s.seed = seed
    def Empty(s):
      return s.drange.Empty()
    def Front(s):
      if ( not s.has_front ):
        s.has_front = 1
        s.seed = dlambda(s.seed, s.drange.Front())
      return s.seed
    def Pop_front(s):
      s.has_front = 0
      cp = s.drange.Save()
      s.drange.Pop_front()
    def Save(s):
      return ReduceImpl(s.drange, s.dlambda, s.seed)
    def __str__(s):
      return f"<Reduce {s.drange}>"
  return _Reduce(copy, dlambda, reduce_seed)

def Reduce(drange, dlambda, seed=None):
  drange = Array(ReduceImpl(drange, dlambda, seed))
  assert ( not drange.Empty() )
  return drange[-1]

def Iota(begin, end, stride=1):
  orange = Range()
  while ( begin < end ):
    orange.Put(begin)
    begin += stride
  return orange

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

def Is_infinite(drange):
  return Is_input(drange) and isinstance(drange.Empty, InfiniteEmpty)

class InfiniteEmpty():
  """ A hack to allow infinite ranges so users don't have to check
      (ifisinstance(s.Empty, int)) and Is_infinite introspection can work
      despite Empty always returning false.
  """
  __call__ = lambda s: False

if ( __name__ == "__main__" ):
  # Test input ranges
  input_range = int|InputRange(10, 20, 30)
  assert(input_range.Front() == 10)
  input_range.Pop_front()
  assert(input_range.Front() == 20)
  input_range.Pop_front()
  input_range.Pop_front()
  assert(input_range.Empty())

  # Test map reduce and filter
  input_range = int|ForwardRange(10, 20, 30)
  mlam = lambda t: t+1;
  assert(Array(Map(input_range, lambda t: t+1)).Length() == 3)
  assert(Reduce(Map(input_range, lambda t: t+1), lambda x, y: x+y) == 63)
  assert(Array(Filter(Map(input_range, lambda t: t+1), lambda x: x>25)).Front() == 31)

  # Test Iota and lots of chained ranges, along with str
  io = Map(Iota(10, 15), lambda t: t - 10)
  while ( not io.Empty() ):
    assert io.Front() == 0
    io.Pop_front()
    io = Map(io, lambda t: t-1)
  assert(io.__str__() == "<Map <Map <Map <Map <Map <Map <InputRange Any>>>>>>>")
  io = Iota(0, 10, 5) # [0, 5]
  io.Pop_front() # 0
  io.Pop_front() # 5
  assert(io.Empty())


  # Test forward ranges and any with range in another, and equality
  fr_range = Any|ForwardRange(10, "hi", int|ForwardRange(10, 20))
  fr_copy = fr_range.Save()
  #   pass
  assert(fr_range.Front() == 10)
  fr_range.Pop_front()
  assert(fr_range.Front() == "hi")
  fr_range.Pop_front()
  assert(fr_range.Front() == int|ForwardRange(10, 20))
  assert(fr_copy == Any|ForwardRange(10, "hi", int|ForwardRange(10, 20)))
  del fr_range, fr_copy

  # Test Random access range
  ra_range = int|RandomAccessRange(10, 20, 30)
  assert(ra_range[1] == 20)
  an_range = ra_range[0:3]
  assert(ra_range._ptr == an_range._ptr)
  an_range[0] = 30
  assert(ra_range[0] != 30)
  assert(ra_range._ptr != an_range._ptr)
  del ra_range, an_range

  # Test static introspection and infinite range
  class FibonacciRange:
    Empty = InfiniteEmpty()
    def __init__(s):  (s.l, s.r) = (1, 0)
    def Pop_front(s): (s.l, s.r) = (s.l+s.r, s.l)
    def Front(s):     return s.l
    def Save(s):
      fib = FibonacciRange()
      (fib.l, fib.r) = (s.l, s.r)
      return fib

  fib = FibonacciRange()
  assert(Is_infinite(fib))
  assert(Is_input(fib))
  assert(Is_forward(fib))
  assert(not Is_bidirectional(fib))
  assert(not Is_random_access(fib))
  fib10 = Take(fib, 10)
  assert(fib10 == Range(1, 1, 2, 3, 5, 8, 13, 21, 34, 55))
  assert(fib10 != Range(1, 1, 2, 3, 5, 8, 13, 21, 34, 44))
  assert(Reduce(fib10, lambda x, y: x+y) == 143)

  # Test concatenate and length with range
  r_range = int|Range(2, 3, 4)
  r_range = r_range + (int|Range(5, 6, 7))
  assert(r_range == Range(2, 3, 4, 5, 6, 7))
  try:
    r_range = r_range + (str|Range("hi"))
    print("ASSERTION ERROR INT+STR")
  except Exception:
    pass

  assert(r_range.Length() == 6)
  r_range.Length(3)
  assert(r_range == Range(2, 3, 4))
  r_range.Length(0)
  assert(r_range.Empty())

  # Test ufcs
  # a = int|ForwardRange(10, 20, 30)
  # assert(a.reduce(lambda x, y: x+y) == reduce(a, lambda x, y: x+y))
  # assert(not a.Empty())
  # del a
  # assert(_memorypool.RSlice_count() == 0)
