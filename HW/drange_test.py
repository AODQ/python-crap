from drange import *
# Test input ranges
input_range = int|InputRange(10, 20, 30)
assert(input_range.Front() == 10)
assert(input_range.Front() == 20)
input_range.Front()
assert(input_range.Empty())
del input_range

# Test map reduce and filter
input_range = int|ForwardRange(10, 20, 30)
mlam = lambda t: t+1;
assert(Array(Map(input_range.Save(), lambda t: t+1)).Length() == 3)
assert(Reduce(Map(input_range.Save(), lambda t: t+1), lambda x, y: x+y) == 63)
assert(Filter(Map(input_range.Save(), lambda t: t+1), lambda x: x>25).Front() == 31)
del input_range

# Test Iota and lots of chained ranges, along with str
io = Map(Iota(10, 15), lambda t: t - 10)
while ( not io.Empty() ):
  assert io.Front() == 0
  io = Map(io, lambda t: t-1)
io = Iota(0, 10, 5) # [0, 5]
io.Front() # 0
io.Front() # 5
assert(io.Empty())
del io


# Test forward ranges and any with range in another, and equality
fr_range = Any|ForwardRange(10, "hi", int|ForwardRange(10, 20))
fr_copy = fr_range.Save()
#   pass
assert(fr_range.Front() == 10)
assert(fr_range.Front() == "hi")
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
  def Front(s):
    (s.l, s.r) = (s.l+s.r, s.l)
    return s.r
  Save  = lambda s: FibonacciRange(s.l, s.r)

fib = FibonacciRange()
assert(Is_infinite(fib))
assert(Is_input(fib))
assert(Is_forward(fib))
assert(not Is_bidirectional(fib))
assert(not Is_random_access(fib))
fib10 = Take(fib, 10)
# assert(fib10 == Range(1, 1, 2, 3, 5, 8, 13, 21, 34, 55))
assert(fib10 != Range(1, 1, 2, 3, 5, 8, 13, 21, 34, 44))
assert(fib10.Reduce(lambda x, y: x+y) == 143)
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
    del t
  except Exception:
    return
  assert(0)
def Exc_assert(left, right):
  try:
    t = left + right
    del t
  except Exception:
    return
  assert(0)

Mak_assert(RangeT(str), Range(str|Range("Hi")))
Mak_assert(int, 2, "hi")
Mak_assert(Variant(int, str), 2, "hi", 3.2342)
Exc_assert(irange, frange)
Exc_assert(vrange2, irange)
Exc_assert(irange, vrange1)
Exc_assert(irange, arange)
Exc_assert(vrange1, arange)
assert(vrange1 + irange  == Range(2, "hi", 2, 3, 4))
assert(vrange1 + srange  == Range(2, "hi", "hi", "there"))
assert(arange  + irange  == Range(2, "hi", 3.0, 2, 3, 4))
assert(arange  + vrange1 == Range(2, "hi", 3.0, 2, "hi"))
assert(arange  + arange  == Range(2, "hi", 3.0, 2, "hi", 3.0))
del irange, frange, srange, arange, vrange1, vrange2, rrange

# Test ufcs
a = int|Range(10, 20, 30)
assert(a.Reduce(lambda x, y: x+y) == Reduce(a.Save(), lambda x, y: x+y))
assert(not a.Empty())
assert(a.Map(lambda x: x+x) == Range(20, 40, 60))
assert(a.Filter(lambda x: x<20) == Range(10))
assert(a.Filter(lambda x: x<20).Map(lambda x: x+x) == Range(20))
assert(a.Filter(lambda x: x<20).Map(lambda x: x+x) == Range(20))
assert((Any|a).Chain(Range(20, 30, 40)) == Range(10, 20, 30, 20, 30, 40))
assert(a.Enumerate().Array()[0][1] == 0)
assert(a.Enumerate().Array()[1][1] == 1)
assert(a.Drop(2) == Range(30))
assert(a.Dropback(1) == Range(10, 20))
b = a.Cycle()
for i in range(0, 50):
  b.Front()
assert(not b.Empty())
assert(a.Chunks(2).Array() == Range(Range(10, 20), Range(30)))
assert(Choose(Range(0), Range(1), True)[0] == 1)
b = Range("A", "B", "C")
c = Zip(a, b)
assert(c.Front() == (10, "A"))
assert(c.Front() == (20, "B"))
c.Front()
assert(c.Empty())
c = Range(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
assert(c.Stride(3) == Range(1, 4, 7, 10))
assert(Stride(Stride(c.Stride(2), 3), 1) == Range(1, 7))
def Sideeffect(s):
  s = 0
assert(c.Tee(lambda s: Sideeffect(s)).Reduce(lambda x, y: x+y) == 66)
assert(c.Retro().Reduce(lambda x, y: x-y) == -44)

from random import *
Generate(random).Take(5).Each(lambda x: print(x))
del a, b, c

Report_leaked_memory()
