from pysat.solvers import Cadical153
from pysat.formula import CNF
import time
import requests

formula_path = 'original.cnf'
backdoor_path = 'backdoors.txt'

start = time.time()

def send_to_telegram(data):
    token = "6972984435:AAGeBAFCALEoz2SXhHLX-uyyj0HWbVny9l8"
    requests.post(
        url='https://api.telegram.org/bot{0}/{1}'.format(token, "sendMessage"),
        data={'chat_id': 277499288, 'text': data}
    )


def backdoor_string_to_list(backdoor_string):
    return list(map(lambda x: x + 1, map(int, backdoor_string.split(':')[1].strip(' \n][').split(', '))))


def next_backdoor(bitvector):
    for i in range(len(bitvector)):
        if bitvector[i] >= 0:
            bitvector[i] = -bitvector[i]
            return bitvector
        else:
            bitvector[i] = -bitvector[i]
    return []

backdoors = []
with open(backdoor_path, 'r') as f:
    for line in f:
        backdoors.append(backdoor_string_to_list(line))
    # print(backdoors)


def _propagate(assumptions):
    # print(base_solver.propagate(assumptions))
    (status, literals) = base_solver.propagate(assumptions)

    # pysat: The status is ``True`` if NO conflict arisen
    # during propagation. Otherwise, the status is ``False``.

    # evoguess: The status is ``True`` if NO conflict arisen
    # during propagation and all literals in formula assigned.
    # The status is ``False`` if conflict arisen.
    # Otherwise, the status is ``None``.

    all_assigned = len(literals) >= base_solver.nof_vars()
    return status and (all_assigned or None), assumptions

def get_unique_lists(lists):
    unique_lists = []
    for l in lists:
        if l not in unique_lists:
            unique_lists.append(l)
    return unique_lists

def merge_backdoors(a, b):
    result = []
    cnt = 0
    for i in range(len(a)):
        for j in range(len(b)):
            merged = merge_list(a[i], b[j])
            # print(merged)
            # print(type(merged))
            if merged:
                status, res = _propagate(merged)
                if status is None:
                    result.append(merged)
    result = filter(lambda x: x != [], result)
    return list(result)

def merge_list(a, b):
    result_set = set(a + b)
    result = list(set(a + b))
    for i in range(len(result)):
        if -result[i] in result_set:
            return []
    return result


# Create a new CNF object from file
formula = CNF(from_file=formula_path)

print("Number of variables: ", formula.nv)

base_solver = Cadical153(bootstrap_with=formula, use_timer=True)

cnt = 0
decart = []

for i in range(len(backdoors)):
    backdoor = backdoors[i]
    results = []
    cnt = 0
    while backdoor != []:
        result, assumps = _propagate(assumptions=backdoor)
        results.append((result, assumps.copy()))
        cnt += 1
        backdoor = next_backdoor(backdoor)
    results = list(filter(lambda x: x[0] is None, results))
    results = list(map(lambda x: x[1], results))
    # print(len(get_unique_lists(results)))
    # print(len(results))
    decart.append(results)


# sort by length desc
decart.sort(key=lambda x: len(x))
print(list(map(len, decart)))
acc = decart[0]
for i in range(1, len(decart)):
    time_merge = time.time()
    acc = merge_backdoors(acc, decart[i])
    # print(acc)
    print("Time to merge: ", time.time() - time_merge)
    filtered = []
    for j in range(len(acc)):
        # print(j, len(decart[i]))
        time_iter = time.time()
        with Cadical153(bootstrap_with=formula) as solver:
            solver.conf_budget(5000)
            # print(decart[i][j])
            solver.solve_limited(assumptions=acc[j])
            if solver.get_status() is None:
                filtered.append(acc[j])
            print("Time to iteration: ", time.time() - time_iter)
            print(len(filtered), "/",  j, "/", len(acc))
            print(solver.accum_stats())
    strs = str((len(acc) - len(filtered)) / len(acc)) + " filtered:" + str(len(filtered)) + " acc:" + str(len(acc))
    send_to_telegram(strs)
    print("sifted: ", (len(acc) - len(filtered)) / len(acc), "filtered:", len(filtered), "acc:", len(acc))
    print("time from start: ", time.time() - start)
    acc = filtered
    if len(filtered) == 0:
        print("SUCCESS")
        break

print(len(acc))
for i in range(len(acc)):
    base_solver.solve(assumptions=acc[i])
    print(base_solver.get_status())
# filter all results that are None
# Solve the formula
# solver.solve()
# print("Time: ", solver.time())
# print("Time: ", solver.time_accum())
print("Time: ", time.time() - start)