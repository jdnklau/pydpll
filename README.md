# PyDPLL - Naive SAT-Solver in Python

Repository contains a DPLL implementation in Python for self-educational
purposes.

PyDPLL is a naive implementation which does not consider any
advanced techniques such as conflict driven clause learning.

## Usage (CLI)

Given a file in DIMACS format, the solver is invoked by

```bash
python3 pydpll.py path/to/file
```

## Usage (inside Python)

```python
import pydpll

cnf_file = 'example.cnf'

phi = pydpll.parse_dimacs(cnf_file)
bindings = phi.solution()
# bindings is a dictionary of variable names to their assignments.
# This dictionary may omit assignments which do not impact the solution.
# For `example.cnf`, the first found solution has no binding for
# the variable '6', meaning the assignment of '6' does not matter.

psi = pydpll.from_list([[1, 2, -3], [-2, 3], [-1], [2]])
print(psi)  # [[1, 2, -3], [-2, 3], [-1], [2]]
print(psi.solution())  # {'1': False, '2': True, '3': True}
```
