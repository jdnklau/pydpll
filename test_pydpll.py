import pydpll


def test_dimacs_parsing_clause_length():
    file = 'example.cnf'
    formula = pydpll.parse_dimacs(file)

    assert len(formula.clauses) == 6


def test_dimacs_parsing_representation():
    file = 'example.cnf'
    formula = pydpll.parse_dimacs(file)

    expected = ("[[1, -2, 3], [-1, -2, 4], [-3, -4, -5],"
                " [-1, 2, 3], [-3, 4, 5], [1, -2, 6]]")
    assert str(formula) == expected


def test_from_list_numbers():
    lst = [[1, 2, -3], [-2, 3], [-1], [2]]
    phi = pydpll.from_list(lst)

    expected = "[[1, 2, -3], [-2, 3], [-1], [2]]"
    assert str(phi) == expected


def test_from_list_str():
    lst = [['a', 'b', '-c'], ['-b', 'c'], ['-a'], ['b']]
    phi = pydpll.from_list(lst)

    expected = "[[a, b, -c], [-b, c], [-a], [b]]"
    assert str(phi) == expected


def test_solve_with_unit_clauses():
    lst = [[1, 2, -3], [-2, 3], [-1], [2]]
    phi = pydpll.from_list(lst)

    assert phi.solution() == {'1': False, '2': True, '3': True}
