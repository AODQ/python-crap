"""
DLang inspired Range implementation in python. Advantages over lists:
  Static Typing with 'Any' and Variant option X
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

"""base Range implementation"""
from drange_primitives import *
from drange_interfaces import *
from drange_functional import *

class Range(RandomAccessRange, OutputRange):
  """ The 'array' implementation of range; giving power of ranges with
      convenience utility functions
  """
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  RStr = lambda s: "Range"
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
  assert(io.__str__() == "Map <Map <Map <Map <Map <Map <Range of Any>>>>>>")
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
    def __init__(s, l=1, r=0):  (s.l, s.r) = (l, r)
    def Pop_front(s): (s.l, s.r) = (s.l+s.r, s.l)
    Front = lambda s: s.l
    Save  = lambda s: FibonacciRange(s.l, s.r)

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
  del fib, fib10, FibonacciRange

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
  del r_range

  # Test variants
  irange  = int|Range(2, 3, 4)
  frange  = float|Range(2.0, 3.0, 4.0)
  srange  = str|Range("hi", "there")
  arange  = Any|Range(2, "hi", 3.0)
  vrange1 = Variant(int, str)|Range(2, "hi")
  vrange2 = Variant(str)|Range("hi")
  rrange  = (RangeT(str))|Range(str|Range("Hi"), str|Range("There"))

  def Mak_assert(qualifier, *args):
    try:
      t = (qualifier)|(Range(*args))
    except Exception:
      return
    assert(0)
  def Exc_assert(left, right):
    try:
      t = left + right
    except Exception:
      return
    assert(0)

  # Mak_assert((RangeT(str))|(Range("hi")))
  # Mak_assert(int, 2, "hi")
  # Mak_assert(Variant(int, str), 2, "hi", 3.2342)
  # Exc_assert(irange, frange)
  # Exc_assert(vrange2, irange)
  # Exc_assert(irange, vrange1)
  # Exc_assert(irange, arange)
  # Exc_assert(vrange1, arange)
  assert(vrange1 + irange  == Range(2, "hi", 2, 3, 4))
  assert(vrange1 + srange  == Range(2, "hi", "hi", "there"))
  assert(arange  + irange  == Range(2, "hi", 3.0, 2, 3, 4))
  assert(arange  + vrange1 == Range(2, "hi", 3.0, 2, "hi"))
  assert(arange  + arange  == Range(2, "hi", 3.0, 2, "hi", 3.0))
  assert(vrange1.__str__() == "Range of Variant (<class 'int'>, <class 'str'>)")

  # Test ufcs
  # a = int|ForwardRange(10, 20, 30)
  # assert(a.reduce(lambda x, y: x+y) == reduce(a, lambda x, y: x+y))
  # assert(not a.Empty())
  # del a
  # assert(_memorypool.RSlice_count() == 0)
