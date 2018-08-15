## Z3 Solver

```
from z3 import *
x = Int('x')
y = Int('y')
solve(x > 2, y < 10, x + 2*y == 7)
# Output: [y = 0, x = 7]
```


Alternatively, we can do

```python
x = Int('x')
y = Int('y')
s = Solver()
s.add(x > 2, y < 10, x + 2*y == 7)
s.check()         # Output: sat
m = s.model()
m[x]              # Output: 7
m[y]              # Output: 0
```


## Reference

- [Z3 API in Python](https://ericpony.github.io/z3py-tutorial/guide-examples.htm)
