from drange import *
"""
ABC | DEF | GHI
JKL | MNO | PQR
STU | VWX | YZ
"""

class File(UFCS_Mixin):
  def __init__(s, fil):
    s.fp = open(fil, 'r', encoding='utf-8')
    s.nline = s.fp.readline()
  Empty = lambda s: s.nline == ''
  def Front(s):
    (t, s.nline) = (s.nline, s.fp.readline())
    return t



phonemap = (Iota(0, 9)
             .Map(lambda t: Range(t*3, t*3+1, t*3+2).Map(lambda s: chr(97+s)).Array())
).Array();
phonemap[8] = Range('w', 'x', 'y', 'z')
print(phonemap)

def PhoneMatch(numrange, strrange):
  if ( numrange.Length() != strrange.Length() ):
    return False
  blah = (Iota(0, numrange.Length())
          .Filter(lambda it: (
              numrange[it].Filter(lambda nr: nr == strrange[it]).Array().Length() > 0
        )))
  return blah.Array().Length() == numrange.Length()

def Plat(nam, amt, afterword, beg):
  print(nam, ", ", amt, ", ", afterword, " -- ", beg)

g = Partial(Plat, "hi", 5);

g("theend", "aee");


while ( True ):
  num = StrRange(input('')[:]).Map(lambda a: int(a)).Array();
  num = num.Map(lambda t: phonemap[t-2]).Array()
  res = (File('dict').Map(lambda dictstr: dictstr[:-1])
                    .Filter(lambda dictstr: PhoneMatch(num, StrRange(dictstr))));
  print(res.Array());
