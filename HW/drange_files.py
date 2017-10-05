from drange import *
import os

class File:
  def __init__(s, fname, _dir):
    s.fname = fname;
    s.is_dir = _dir;


class Directory:
  def __init__(s, dirname):
    s.dirname = dirname

class _Walk(UFCS_Mixin):
  def __init__(s, fils):
    s.fils = fils
  Empty = lambda s: len(s.fils) == 0
  def Front(s):
    if ( not isinstance(s.fils[-1], str) ):
      fil = s.fils[-1].Front()
      if ( s.fils[-1].Empty() ):
        s.fils.pop()
      return fil
    else:
      fil = s.fils.pop()
      is_dir = os.path.isdir(fil);
      if ( is_dir ):
        s.fils += [Walk(fil).Map(lambda x: File(fil + '/' + x.fname, x.is_dir))];
      return File(fil, is_dir)
  Save  = lambda s: _Walk(s.fils[:])

def Walk(dirname):
  return _Walk(os.listdir(dirname))

def Valid_py_extension ( fil ):
  return re.match("\.[pP][yY]")

def REX(str, pat):
  from re import search
  return search(pat, str) != None

def Readline(fname, count):
  _str = ""
  fp = open(fname, 'r', encoding='utf-8')
  for i in range(0, 10):
    g = fp.readline()
    if ( g == '' ): break
    _str += g
  return _str

def Proper_Py(_str):
  try:
    g = Readline(_str, 10)
  except Exception: # mostly for binary files
    return False
  return REX(_str, r"\.[pP][yY]") or (
    REX(g, r"from \w* import \w*") or
    REX(g, r"from \w* import \*") or
    REX(g, r"import \w*")
    )

from re import match
for i in Walk('.').Filter(lambda t: not t.is_dir and Proper_Py(t.fname)):
  print('i: ', i.fname)

"""
Program searches for python source code
.py cases no matter
prints every file with regex
from \w* import \w*
from \w* import \*

anywhere in first 10 lines
"""
  
