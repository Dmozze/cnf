import itertools


def all_clauses(length):
    count = 2 ** length
    clauses = []
    for i in range(count):
        clause = []
        for j in range(length):
            if i & (1 << j):
                clause.append(j + 1)
            else:
                clause.append(-(j + 1))
        clauses.append(clause)
    return clauses

def all_sets_of_clauses(length):
    all = all_clauses(length)
    sets = []
    for i in range(1, len(all)):
        sets += list(itertools.combinations(all, i))
    # tuple to list
    sets = [list(x) for x in sets]
    return sets

def get_truth_table_by_clauses_set_dnf(clauses):
    unique_literals = set()
    for clause in clauses:
        for literal in clause:
            unique_literals.add(abs(literal))
    unique_literals = list(unique_literals)
    truth_table = [0] * (2 ** len(unique_literals))
    for i in range(2 ** len(unique_literals)):
        assignment = []
        for j in range(len(unique_literals)):
            if i & (1 << j):
                assignment.append(unique_literals[j])
            else:
                assignment.append(-unique_literals[j])
        clause_value_all = False
        for clause in clauses:
            clause_value = True
            for literal in clause:
                if literal in assignment:
                    clause_value = False
                    break
            if clause_value:
                clause_value_all = True
                break
        if clause_value_all:
            truth_table[i] = 1
    return truth_table

def get_truth_table_by_clauses_set_cnf(clauses):
    unique_literals = set()
    for clause in clauses:
        for literal in clause:
            unique_literals.add(abs(literal))
    unique_literals = list(unique_literals)
    truth_table = [0] * (2 ** len(unique_literals))
    for i in range(2 ** len(unique_literals)):
        assignment = []
        for j in range(len(unique_literals)):
            if i & (1 << j):
                assignment.append(unique_literals[j])
            else:
                assignment.append(-unique_literals[j])
        clause_value_all = True
        for clause in clauses:
            clause_value = False
            for literal in clause:
                if literal in assignment:
                    clause_value = True
                    break
            if not clause_value:
                clause_value_all = False
                break
        if clause_value_all:
            truth_table[i] = 1
    return truth_table


def get_map_to_dnf():
    cnfs = []
    dnfs = []
    clause = []
    for clauses in all_sets_of_clauses(2):
        clause.append(clauses)
        cnfs.append(get_truth_table_by_clauses_set_cnf(clauses))
        dnfs.append(get_truth_table_by_clauses_set_dnf(clauses))

    map_dnf_to_cnf = dict()
    for i in range(len(dnfs)):
        for j in range(len(cnfs)):
            if dnfs[i] == cnfs[j]:
                map_dnf_to_cnf[i] = j
                fuck = False
    return map_dnf_to_cnf

print(all_sets_of_clauses(2))


def map_values_to_cnf(first, second, formula):
    result = []
    for clause in formula:
        result.append([])
        for literal in clause:
            if literal == 1:
                result[len(result) - 1].append(first)
            if literal == -1:
                result[len(result) - 1].append(-first)
            if literal == 2:
                result[len(result) - 1].append(second)
            if literal == -2:
                result[len(result) - 1].append(-second)
    return result

def map_values_from_cnf(first, second, formula):
    result = []
    for clause in formula:
        result.append([])
        for literal in clause:
            if literal == first:
                result[len(result) - 1].append(1)
            if literal == -first:
                result[len(result) - 1].append(-1)
            if literal == second:
                result[len(result) - 1].append(2)
            if literal == -second:
                result[len(result) - 1].append(-2)
    return result



