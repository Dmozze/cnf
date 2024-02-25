import sys

from pysat.solvers import Cadical153
from pysat.formula import CNF
import time

from utils.telegram import send_to_telegram

formula_path = 'original.cnf'
start = time.time()

formula = CNF(from_file=formula_path)
solver = Cadical153(bootstrap_with=formula.clauses)

solver.solve()

print("Time: ", time.time() - start)

statistics = dict()
statistics['name'] = sys.argv[1]
statistics['time_to_dumpy'] = time.time() - start
statistics['success'] = True
send_to_telegram(statistics)
