


class A:
  def __init__(s):
    print("A Once only!")

class B(A):
  def __init__(s):
    super().__init__()
    print("B Once only!")

class C(A):
  def __init__(s):
    super().__init__()
    print("C Once only!")


class D(B, C):
  def __init__(s):
    super().__init__()
    print("D Once only!")

print("A----")
A()
print("B----")
B()
print("D----")
D()
