from drange import *

print("is infinite 12 12 12.. ", Is_infinite(Range(12).Cycle()))
# for x in Range(12).Cycle(): print(x)

for x in StrRange('Hello'): print(x, end=", ")
print()

for i in Range(2, 3, 4, 5, 6).Map(lambda l: l*4): print(i, end=", ")
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
