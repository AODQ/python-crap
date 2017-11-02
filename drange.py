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


# utilities to move elsewhere
def Partial(fname, *args):
  class _Partial(object):
    def __init__(s, fhandle, *args):
      s.fhandle = fhandle;
      s.args  = args;
    def __call__(s, *args):
      return s.fhandle(*s.args, *args)
  return _Partial(fname, *args);

" -- everything below is from the link -- "
"https://gist.github.com/divs1210/d218d4b747b08751b2a232260321cdeb"
" lots of good lisp-like stuff from there "
def Y(g):
  ' y combinator '
  exp = lambda f: g(lambda arg: f(f)(arg))
  return (exp)(exp)

def Cond(cond_body_pairs, _else=lambda: None):
  'functional if-elif..-else expression'

def If(cond, then, _else = lambda: None):
  return Cond((cond, then), _else);

def Let(bindings, body, env = None):
  ' introduce local bindings '
  if ( len(bindings) == 0 ):
    return body(env);
  env = env or _obj()
  k, v = bindings[:2]
  if ( isinstance(v, types.FunctionType) ):
    v = v(env);
  setattr(env, k, v)
  return Let(bindings[2:], body, env);

def FOR(bindings, body, env=None):
  'Clojure style List comprehension.'
  if len(bindings) == 0:
    tmp = body(env)
    return [] if tmp is _FILLER else [tmp]

  env = env or _obj()
  k, v = bindings[:2]
  if k == ':IF':
    cond = v(env)
    return FOR(bindings[2:],
               lambda e: body(e) if cond else _FILLER,
               env)
  elif k == ':LET':
    return LET(v,
               lambda e: FOR(bindings[2:], body, e),
               env)
  elif k == ':WHILE':
    if v(env):
      return FOR(bindings[2:], body, env)
    else:
      return []
  elif isinstance(v, types.FunctionType):
    v = v(env)

  res = []
  for x in v:
    setattr(env, k, x)
    res += FOR(bindings[2:], body, env)
    delattr(env, k)

  return res


# you can not run this otherwise it complains about UFCS mixin not
# being defined.
if ( __name__ == "__main__" ):
  pass
