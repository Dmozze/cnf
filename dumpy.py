import sys

import requests
from pysat.solvers import Cadical153
from pysat.formula import CNF
import time

formula_path = 'original.cnf'
start = time.time()

def send_to_telegram(data):
    token = "6972984435:AAGeBAFCALEoz2SXhHLX-uyyj0HWbVny9l8"
    string = str(data)
    # add \n after each key-value pair
    string = string.replace(", ", "\n")
    # remove { and }
    string = string.replace("{", "")
    string = string.replace("}", "")
    if sys.argv[2] == "false":
        if 'success' not in data and 'time_to_load' not in data:
            return


    requests.post(
        url='https://api.telegram.org/bot{0}/{1}'.format(token, "sendMessage"),
        data={'chat_id': 277499288, 'text': string}
    )

formula = CNF(from_file=formula_path)
solver = Cadical153(bootstrap_with=formula.clauses)

solver.solve()

print("Time: ", time.time() - start)

statistics = dict()
statistics['name'] = sys.argv[1]
statistics['time_to_dumpy'] = time.time() - start
statistics['success'] = True
