from drange import *
from drange_interfaces import *
from drange_primitives import *
from drange_functional import *

# Iterate that always returns 12
class Twelve:
  Empty = InfiniteEmpty()
  __init__ = lambda s: None
  Save = Pop_front = lambda s: s
  Front  = lambda s: 12

twelve = Add_Python_Iterator(Twelve())
print("should be 12 12 12 12 12 12 ... ")
# for x in twelve:
#   print("X: ", x)

hello = Add_Python_Iterator(Range("Hello"))
print("Should be hello")
for x in hello:
  print(x)

class Double:
  def __init__(s, l):
    s.l = l.Save()
  Empty = lambda s: s.l.Empty()
  Front = lambda s: s.l.Front()*2
  Pop_front = lambda s: s.l.Pop_front()
  Save = lambda s: Double(s.l)

double_list = Add_Python_Iterator(Double(Range(*[2, 3, 4])))
double = Add_Python_Iterator(Double(Range(2, 3, 4)))
print("Should be 4 6 8")
for x in double_list:
  print(x)
for x in double:
  print(x)

just_letters = Add_Python_Iterator(Array(Filter(Range(2, 'a', 'b', 3, 5),
                                   lambda s: type(s) == str)))
print("just letters")
for x in just_letters:
  print(x)

class Wspace:
  def __init__(s, _str):
    s.l = str(_str).split(" ") # drange doesn't have split yet
  Empty = lambda s: len(s.l) == 0
  Front = lambda s: s.l[-1]
  Pop_front = lambda s: s.l.pop()
  Save = lambda s: Wspace(" ".join(s.l))

s = 'I love cheese blah blah blah'
print(str(s))
whitespace = Add_Python_Iterator(Wspace(s))
print("whitespace")
for x in whitespace:
  print(x)
