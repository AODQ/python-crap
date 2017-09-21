from drange import *

print("is infinite 12 12 12.. ", Is_infinite(Range(12).Cycle()))
# for x in Range(12).Cycle(): print(x)

for x in StrRange('Hello'): print(x, end=", ")
print()

# this is now a lazy range that can be iterated
double = (Range(2, 3, 4).Map   (lambda l: l*4)
                        .Filter(lambda t: t >= 0)
                        .Tee   (lambda t: print("(lazy: ", t, end="), "))
                        .Map   (lambda t: t//2)
)
print("double list name: ", double)
print("has iter attrib? ", hasattr(double, "__iter__")) #t
print("has next attrib? ", hasattr(double, "__next__")) #f
print("iter has next attrib? ", hasattr(double.__iter__(), "__next__")) #t
for i in double: print(i, end=", ")
print()

print("Just letters --")
for x in Range(2, 'a', 'b', 3, 5).Filter(lambda s: type(s) == str):
  print(x, end=", ")
print()


for x in StrRange('I love D Ranges').Split(lambda s: s==' '):
  print(x.To_str(commas=False), end=", ")
print()
del double
del x

Report_leaked_memory()
