import sys




class Var:
    def __init__(self, name):
        self.name = name
        self.value = None

    def __str__(self):
        return self.name


class Literal:
    def __init__(self, var, polarity=True):
        self.var = var
        self.polarity = polarity  # False if negated.

    def __str__(self):
        name = str(self.var.name)
        name = "-" + name if not self.polarity else name
        return name

    def eval(self):
        return self.var.value == self.polarity

    def value(self):
        return self.var.value

    def set_value(self, value):
        self.var.value = value

    def __neg__(self):
        return Literal(self.var, not self.polarity)


class Formula:
    """
    Formula class.
    It is recommended to use the from_list() or parse_dimacs() functions
    to generate a Formula object.
    """
    def __init__(self, clauses, verbose=False):
        self.clauses = clauses
        self.vars = self._collect_vars(clauses)

        # List of sets of variables to reset when backtracking.
        self.reset_stack = [(clauses, set())]
        self.choice_stack = []  # Stack of variables during backtracking.

        self.verbose = verbose

    def _collect_vars(self, clauses):
        vars = {}
        for clause in clauses:
            for literal in clause:
                vars[literal.var.name] = literal.var
        return vars

    def __str__(self):
        inners = []
        for clause in self.clauses:
            inners += ['[' + ", ".join([str(l) for l in clause]) + ']']
        return '[' + ", ".join(inners) + ']'

    def eval(self):
        for clause in self.clauses:
            if len(clause) == 0:
                return False
            for literal in clause:
                if literal.eval():  # If any literal is True, the clause is True.
                    break
            else:
                return False
        return True

    def _unit_propagate(self):
        for clause in self.clauses:
            if len(clause) == 1:
                literal = clause[0]
                # Safety check!
                if literal.value() == None:
                    if self.verbose:
                        print("Unit propagate: ",
                              literal.var.name, literal.polarity)
                    literal.set_value(literal.polarity)
                    _, reset_set = self.reset_stack[-1]
                    reset_set.add(literal.var)
                    return True
        return False

    def _simplify(self):
        print("Simplify with ",
                {v.name: v.value for v in self.vars.values() if v.value != None})
        changed = False
        new_clauses = []
        for clause in self.clauses:
            is_solved = any([l.eval() for l in clause])

            if is_solved:
                continue

            # Only keep free variables.
            nc = [l for l in clause if l.value() == None]
            print("Clause: ", {l.var.name: l.value() for l in nc})
            new_clauses.append(nc)

            if nc != clause:
                changed = True

        self.clauses = new_clauses
        return changed

    def solution(self):
        changed = True
        if self.verbose:
            print("Solving: ", self)
        while changed:
            changed = False
            unit_propagated = self._unit_propagate()
            changed = unit_propagated
            while unit_propagated and self._simplify():
                if any([len(c) == 0 for c in self.clauses]):
                    break
                unit_propagated = self._unit_propagate()

            if self.verbose and changed:
                print("Solving: ", self)

            if self.clauses == []:
                return {v.name: v.value for v in self.vars.values() if v.value != None}
            elif any([len(c) == 0 for c in self.clauses]):
                if self.choice_stack == []:
                    return None
                else:
                    self._backtrack()
                    changed = True
                    if self.verbose:
                        print("Solving: ", self)
            elif any([v.value == None for v in self.vars.values()]):
                self._choose_literal()
                changed = True
                if self.verbose:
                    print("Solving: ", self)
            else:
                if self.verbose:
                    print("No solution found, but no free variables left.")
                return None

        return None

    def has_solution(self):
        return self.solution() is not None

    def _choose_literal(self):
        literal = self.clauses[0][0]
        literal.set_value(literal.polarity)
        if self.verbose:
            print("Choose literal: ", literal.var.name, literal.polarity)
        self.choice_stack.append(literal)
        self.reset_stack.append((self.clauses, set()))

        self._simplify()

    def _backtrack(self):
        lit = self.choice_stack.pop()
        lit.set_value(not lit.value())  # Flip the value.
        if self.verbose:
            print("Backtrack: ", lit.var.name, lit.value())
        self.clauses, reset_set = self.reset_stack.pop()
        for v in reset_set:
            v.value = None
        if self.choice_stack != []:
            _, reset_set = self.reset_stack[-1]
            reset_set.add(lit.var)
        self._simplify()

    def var_assignments(self):
        return [v.value for v in self.vars.values()]


def parse_dimacs(filename, verbose_formula=False):
    """
    Parse a DIMACS file and return a Formula object.

    See file format description from SAT competition 2011
    http://www.satcompetition.org/2011/format-benchmarks2011.html
    """
    clause_vars = []
    clauses = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('c'):
                continue
            elif line.startswith('p'):
                _, _, nbvar, nbclauses = line.split()
                nbvar = int(nbvar)
                nbclauses = int(nbclauses)

                # Setup variables.
                for i in range(1, nbvar + 1):
                    clause_vars.append(Var(str(i)))
            elif line.startswith('%') or len(line) == 0 or line == "\n":
                break
            else:
                clause = []
                for var in line.split():
                    if var == "":
                        continue
                    var = int(var)
                    if var == 0:
                        break
                    polarity = var > 0
                    clause.append(Literal(clause_vars[abs(var) - 1], polarity))
                clauses.append(clause)
    return Formula(clauses, verbose_formula)


def from_list(clauses, verbose_formula=False):
    """
    Manually type the formula as a nested list, for example:
        [[1, 2, -3], [-2, 3], [-1], [2]]
    or
        [['a', 'b', '-c'], ['-b', 'c'], ['-a'], ['b']]

    The outer list is a list of clauses, and each clause is a list of
    literals. Each literal is either a string or an integer.
    Polaroty is determined by either the sign of the integer
    (-1 represents "not 1") or the presence of a "-"-prefix in strings.
    """
    clause_vars = {}
    parsed_clauses = []
    for clause in clauses:
        parsed = []
        for name in clause:
            polarity = __var_polarity(name)
            name = __var_name(name)
            if name not in clause_vars:
                clause_vars[name] = Var(name)
            var = clause_vars[name]
            lit = Literal(var, polarity)
            parsed.append(lit)
        parsed_clauses.append(parsed)
    return Formula(parsed_clauses, verbose_formula)

def __var_name(name):
    if isinstance(name, str):
        if name.startswith("-"):
            return name[1:]
        else:
            return name
    else:
        return str(abs(name))

def __var_polarity(name):
    if isinstance(name, str):
        return not name.startswith("-")
    else:
        return name > 0


if __name__ == "__main__":
    if len(sys.argv) not in [2,3]:
        print("Usage: python3 pydpll.py [-v] <filename>")
        sys.exit(1)
    elif len(sys.argv) == 3:
        verbose = sys.argv[1] == "-v"
        filename = sys.argv[2]
    else:
        verbose = False
        filename = sys.argv[1]

    formula = parse_dimacs(filename, verbose_formula=verbose)
    print(formula.solution())
