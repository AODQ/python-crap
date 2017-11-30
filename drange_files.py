from drange import *

class File(UFCS_Mixin):
  def __init__(s, fil):
    s.fp = open(fil, 'r', encoding='utf-8')
    s.nline = s.fp.readline()[:-1]
  Empty = lambda s: s.nline == ''
  def Front(s):
    (t, s.nline) = (s.nline, s.fp.readline()[:-1])
    return t
