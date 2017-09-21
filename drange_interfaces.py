""" An object-based interface for ranges [with memory pool] """
from drange_primitives import *
from drange_interfaces import *

class __MemoryPool:
  """
  A range slice is only a view on memory, it does not create a new copy, however
  if a modification is made to the memory pool where multiple viewers exist, a
  copy will be made. The memory is freed using refcounts
  """
  def __init__(s):
    (s._mempool, s._freemem, s._counter) = ({}, [], 0)
    #{ID : [refcount, memory]}
  def Report_leaked_memory(s):
    import gc
    # I have to collect a few times, in order to be more accurate, because
    # for whatever reason not everything is collected though I've asked.
    # If you remove `del` in Deallocate you can see for yourself that this
    # doesn't touch __MemoryPool memory
    gc.collect()
    gc.collect()
    gc.collect()
    print("MEMORY LEAK REPORT -------------------------------")
    cnt = 0
    for leak in s._mempool:
      cnt = 1
      print("LEAK ID: ", leak)
      print("   count:  ", s._mempool[leak][0])
      print("   memory: ", s._mempool[leak][1])
    if ( not cnt ):
      print("No leaks")
    print("--------------------------------------------------")
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
    """ USAGE: ptr = Selement, if element=None removes it """
    ptr = s.Touch(ptr, dealloc=1)
    if ( element == None ):
      del s._mempool[ptr][1][index]
    else:
      s._mempool[ptr][1][index] = element
    return ptr
  def RElement(s, ptr, index):
    return s._mempool[ptr][1][index]

_memorypool = __MemoryPool()
def Report_leaked_memory():
  _memorypool.Report_leaked_memory()

class _Any:
  __str__ = lambda s: "Any"
  Valid_Instance = lambda s, o: True
Any = _Any()
Any._types = tuple([Any])

class Variant:
  " Variant using built-in python tuple, not ranges "
  def __init__(s, *args):
    s._types = tuple(args)
  __str__ = lambda s: f"Variant {s._types}"
  def Valid_Instance(s, oinst):
    assert(not isinstance(oinst, type))
    for t in s._types:
      if ( hasattr(t, "Valid_Instance") ):
        if ( t.Valid_Instance(oinst) ):
          return True
      elif ( issubclass(t, type(oinst)) ):
        return True
    return False

def Valid_Type_Superset(ltype, rtype):
  (amt, g) = (0, len(rtype._types)-1)
  for i in rtype._types:
    amt += (i in ltype._types)
  return amt == len(rtype._types)

class RangeT(Variant):
  " Range type "
  def __init__(s, *args):
    s._types = Variant(*args)
  def Valid_Instance(s, oinst):
    if ( not isinstance(oinst, TemplateRange) ):
      return False
    if ( not Valid_Type_Superset(s._types, oinst._type) ):
      return False
    for val in _memorypool._mempool[oinst._ptr][1]:
      if ( not s._types.Valid_Instance(val) ):
        return False
    return True
  __str__ = lambda s: f"RangeT {s._types}"

def Translate_type(type):
  return type if (isinstance(type, Variant) or isinstance(type, _Any))else(
                 Variant(type))

class TemplateRange():
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
  def __or__(s, type):
    return type|s
  def __ror__(s, type):
    """ Type check """
    s._type = Translate_type(type)
    for i in _memorypool._mempool[s._ptr][1]:
      assert(s._type.Valid_Instance(i))
    return s
  RStr = lambda s: ""
  __str__ = lambda s: f"{s.RStr()} of {s._type}"
  def Compatible(s, o):
    "Returns if the type of s is a superset of o [for say, s+o]"
    if   ( isinstance(s._type, _Any) ): return True
    elif ( isinstance(o._type, _Any) ): return False
    return Valid_Type_Superset(s._type, o._type)

class _FakeFront():
  """To allow: myrange.Front() , or myrange.Front.Set(5)"""
  def __init__(s, trange):
    s._trange = trange
  def Invariant(s):
    assert s._trange.begin < s._trange.end
  def __call__(s):
    s.Invariant()
    val = _memorypool.RElement(s._trange._ptr, s._trange.begin)
    s._trange.begin += 1
    return val
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
  RStr = lambda s: "InputRange"

class ForwardRange(InputRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  RStr = lambda s: "ForwardRange"
  def Save(s):
    sav = (type(s))(noalloc=True)
    sav._type = s._type
    (sav.begin, sav.end) = (s.begin, s.end)
    sav._ptr = s._ptr
    _memorypool.Slice(sav._ptr)
    return sav
  def __eq__(s, o):
    savs = s.Save()
    from drange_primitives import Is_input
    if ( not Is_input(o) ):
      return False
    savo = o.Save()
    while ( not savs.Empty() and not savo.Empty() ):
      if ( savs.Front() != savo.Front() ):
        return False
    return savs.Empty() and savo.Empty()

class BidirectionalRange(ForwardRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  RStr = lambda s: "BidirectionalRange"
  def Back(s):
    assert not s.Empty()
    s.end -= 1
    return _memorypool.RElement(s._ptr, s.end)

class RandomAccessRange(BidirectionalRange):
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  RStr = lambda s: "RandomAccessRange"
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

class OutputRange(InputRange):
  RStr = lambda s: "OutputRange"
  def __init__(s, *args, noalloc=None):
    super().__init__(*args, noalloc=noalloc)
  def Put(s, element):
    s._ptr = _memorypool.PushElement(s._ptr, element)
    s.end += 1
