from dataclasses import dataclass
from copy import copy, deepcopy

@dataclass
class A:
	v2: int

@dataclass
class B:
	a: A
	v1: int

a = A(1)
b = B(a, 2)

c = copy(b)
d = deepcopy(b)

print(id(b), id(a))
print(id(c), id(c.a))
print(id(d), id(d.a))