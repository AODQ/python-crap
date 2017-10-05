"""
DLang inspired Range implementation in python. Advantages over lists:
  Static Typing with 'Any' and Variant option X
  Memory pool [Slices do not copy unless modified] X
  Many different range types:
    Input, Forward, Bidirectional, Random Access X
    Output, Assignable, Infinite                 X
  Introspection functions (Is_input, Is_infinte, etc) X
  "UFCS"-optional chaining functions [upper-case = supported]:
    Map, Filter, Reduce, Chain, Enumerate, Drop, Dropback, Cycle, Iota, Chunks,
    Choose, Zip, Stride, Tee, Take, Array, and Retro
  To change size, just write to a range's length X
Other things:
  + to concatenate, == for equality. X
Restrictions:
  python lists, maps, dicts, etc are not allowed in a range
"""

"""base Range implementation"""
from drange_functional import *
from drange_primitives import *
from drange_interfaces import *

class Range(RandomAccessRange, OutputRange, UFCS_Mixin):
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
    return s.end-s.begin

  def To_str(s, commas=True):
    _str = ""
    for i in PyIter(s):
      _str += f"{i}" + ["",", "][commas]
    if ( s != "" and commas ):
      _str = _str[0:-2]
    return _str
  def __str__(s):
    return str(s._type) + "|[" + s.To_str() + "]"
  def __add__(s, o):
    assert(s.Compatible(o))
    if ( Is_input(o) ):
      (dfrom, dto) = (o.Save(), s.Save())
      while ( not dfrom.Empty() ):
        dto.Put(dfrom.Front())
      return dto
    else:
      dto = s.Save()
      dto.Put(o)
      return dto


# you can not run this otherwise it complains about UFCS mixin not
# being defined.
if ( __name__ == "__main__" ):
  pass
