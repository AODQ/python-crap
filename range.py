"""
DLang inspired Range implementation in python. Advantages over lists:
  Static Typing with 'Any' and Variant option
  Memory pool [Slices do not copy unless modified]
  Many different range types:
    Input, Forward, Bidirectional, Random Access
    Output, Assignable, Infinite
  Introspection functions (Is_input_range, Is_infinte, etc)
  "UFCS"-optional chaining functions:
    map, filter, reduce, chain, enumerate, drop, dropback, cycle, iota, chunks,
    choose, zip, stride, tee, take, array, and retro
  To change size, just write to a range's length
Other things:
  + to concatenate, == for equality.
Restrictions:
  python lists, maps, dicts, etc are not allowed in a range
"""

class __MemoryPool:
  """
  A range slice is only a new view on memory, it does not create a new copy,
  however if a modification is made to the memory pool where multiple viewers
  exist, a copy will be made. The memory is freed using refcounts
  """
  def __init__(self):
    self.__mempool = []
  def Report_leaked_memory(self):
    pass
  def RSlice_count(self):
    pass
__memorypool = __MemoryPool()

class Variant:
  def __init__(self, *args):
    self._types = *args

class InputRange:
  def __init__(self, *args):
    self._type = "Any"
  def __ror__(self, type):
    self._type = type
    return self


if ( __name__ == "__main__" ):
  # Test input ranges
  input_range = 'int'|InputRange(10, 20, 30)
  assert(input_range.Front() == 10)
  input_range.Pop_front()
  assert(input_range.Front() == 20)
  input_range.Pop_front()
  input_range.Pop_front()
  assert(input_range.Empty())
  del input_range;
  assert(__memorypool.RSlice_count() == 0)

  # Test forward ranges and any with range in another
  fr_range = 'Any'|ForwardRange(10, "hi", 'int'|ForwardRange(10, 20))
  fr_copy = fr_range.Save()
  while ( not fr_range.Empty() ):
    pass
  assert(fr_copy.Front() == 10)
  del fr_range, fr_copy
  assert(__memorypool.RSlice_count() == 0)

  # Test Random access range, slices and memory pool
  ra_range = 'int'|RandomAccessRange(10, 20, 30)
  assert(ra_range[1] == 20)
  an_range = ra_range[0:3]
  assert(ra_range.RID() == an_range.RID())
  an_range[0] = 30
  assert(ra_range.RID() != an_range.RID())
  del ra_range, an_range
  assert(__memorypool.RSlice_count() == 0)

  # Test ufcs
  a = 'int'|ForwardRange(10, 20, 30)
  assert(a.reduce(lambda x, y: x+y) == reduce(a, lambda x, y: x+y))
  assert(not a.Empty())
  del a
  assert(__memorypool.RSlice_count() == 0)


  # Test static introspection and infinite range
  class FibonacciRange:
    empty = false
    __init__(s):      (s.l, s.r) = (1, 0)
    def Pop_front(s): (s.l, s.r) = (s.l+s.r, s.l)
    def Front(s):     return s.l

  FibonacciRange fib;
  fib10 = fib.take(10).array() # Get 10 of fib and make it an array
  assert(fib10 == Range(1, 1, 2, 3, 5, 8, 13, 21, 34, 55))
  assert(Is_infinite(fib))
  assert(Is_forward_range(fib))
  del FibonacciRange, fib10, fib
  assert(__memorypool.RSlice_count() == 0)

  # Test concatenate and length with range
  r_range = 'int'|Range(2, 3, 4)
  r_range = r_range + 'int'|Range(2, 3, 4)
  try:
    r_range = r_range + 'string'|Range("hi")
    assert(0)
  except Exception:
    pass

  try:
    r_range = r_range + 'int'|Range("hi")
    assert(0)
  except Exception:
    pass

  assert(r_range.length == 6)
  r_range.length = 3
  assert(r_range == Range(2, 3, 4))
