from pysat.solvers import Cadical153
from pysat.formula import CNF
import time

formula_path = 'original.cnf'
start = time.time()

formula = CNF(from_file=formula_path)
solver = Cadical153(bootstrap_with=formula.clauses)

solver.solve()

print("Time: ", time.time() - start)
