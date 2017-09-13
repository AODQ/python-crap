# generic functios to make python more sane

from functools import *

def ReduceForce(lam, lis, zero, one):
  " Defines cases on zero and one.. so it must reduce and not crash "
  return [zero, one][len(lis)] if len(lis) < 2 else reduce(lam, lis)

ApplyL = lambda x, y: list (map(x, y))
ApplyT = lambda x, y: tuple(map(x, y))
Zipget = lambda lis, ind: ApplyL(lambda tup: tup[ind], lis)
def If_type(lval, rval, itrue, ifalse):
  "If lval is rval, returns itrue otherwise ifalse.."
  return [ifalse, itrue][isinstance(lval, type(rval))]

from forbiddenfruit import curse 

tfunc_map = {
  "Filter": lambda s, f: filter(f, list(s)),
  "Reduce": lambda s, f: reduce(f, list(s)),
  "Map":    lambda s, f: map   (f, list(s)),
  "ApplyL": lambda s, f: list(s.Map(f)),
  "ApplyT": lambda s, f: list(s.Map(f)),
  "Zipget": lambda s, i: s.ApplyL(lambda tup: tup[i]),
  "ReduceForce": lambda s, fambda, izero, ione:
      [izero, ione][len(s)] if len(s) < 2 else s.Reduce(fambda)
}
ttype_list = [list, map, filter, tuple]

for ttype in ttype_list:
  for tfunc in tfunc_map:
    curse(ttype, tfunc, tfunc_map[tfunc])

del tfunc_map, ttype_list

if ( __name__ == "__main__" ):
  assert  (2, 3, 4).Reduce(lambda x, y: x + y) == 9
  assert ([2, 3, 4].Map(lambda x: x+x)
                   .Filter(lambda t: t > 5)
                   .Reduce(lambda x, y: x+y))
