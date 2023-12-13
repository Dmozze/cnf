from pysat.solvers import Cadical153
from pysat.formula import CNF
import sys
import time
import requests

from telegram import send_to_telegram

formula_path = 'original.cnf'
backdoor_path = 'backdoors.txt'

start = time.time()

prop_hit = 0


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
    global prop_hit
    result = []
    for i in range(len(a)):
        for j in range(len(b)):
            merged = merge_list(a[i], b[j])
            # print(merged)
            # print(type(merged))
            if merged:
                status, res = _propagate(merged)
                if status is None:
                    result.append(merged)
                else:
                    prop_hit = prop_hit + 1
    result = filter(lambda x: x != [], result)
    return list(result)


def merge_list(a, b):
    result_set = set(a + b)
    result = list(set(a + b))
    for i in range(len(result)):
        if -result[i] in result_set:
            return []
    return result

def get_unique_literals(lists):
    unique_literals = set()
    for l in lists:
        for i in range(len(l)):
            if l[i] not in unique_literals:
                unique_literals.add(l[i])
    return unique_literals

def avg_length(backdoor):
    return sum(map(len, backdoor)) / len(backdoor)


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

statistics = dict()
statistics['name'] = sys.argv[1]
statistics['time_to_load'] = round(time.time() - start)
send_to_telegram(statistics, sys.argv[2])

# sort by length desc
one_hard = list(map(lambda x: x[0], filter(lambda x: len(x) == 1, decart)))
if one_hard:
    all_one_hard = one_hard[0]
    for i in range(1, len(one_hard)):
        all_one_hard = merge_list(all_one_hard, one_hard[i])
    statistics = dict()
    statistics['name'] = sys.argv[1]
    statistics['one_length'] = len(one_hard)
    statistics['one_vars'] = len(all_one_hard)
    send_to_telegram(statistics, sys.argv[2])
    if all_one_hard:
        for i in range(len(all_one_hard)):
            base_solver.add_clause([all_one_hard[i]])
    else:
        print("UNSAT")
        exit()
print("len" + str(len(one_hard)))
hards = list(filter(lambda x: len(x) > 1, decart))
hards.sort(key=lambda x: len(x))
statistics = dict()
statistics['name'] = sys.argv[1]
statistics['hards_length'] = len(hards)
flat_list = [item for sublist in hards for item in sublist]
kek = [item for sublist in flat_list for item in sublist]
statistics['hards_vars'] = len(hards)
send_to_telegram(statistics, sys.argv[2])

# print(list(map(len, decart)))
hards_to_merge = hards.copy()
hards_to_merge.pop(0)
acc = hards[0]
for i in range(1, len(hards)):
    prop_hit = 0
    time_merge = time.time()
    vars_acc = get_unique_literals(acc)
    # choice best backdoor by avg length
    acc_avg_len = avg_length(acc)
    acc_length = avg_length(acc)
    acc_len = (avg_length(get_unique_lists(merge_backdoors(acc, hards_to_merge[0]))) - acc_avg_len) / len(get_unique_lists(merge_backdoors(acc, hards[i])))
    avg_best_index = 0

    for j in range(len(hards_to_merge)):

        next = get_unique_lists(merge_backdoors(acc, hards_to_merge[j]))
        next_len = len(next)
        next_literals = get_unique_literals(next)
        comprasion = (avg_length(next) - acc_avg_len) / next_len
        if (avg_length(next) - acc_avg_len) / next_len > acc_len:
            avg_best_index = j
            acc_len = (avg_length(next) - acc_avg_len) / next_len

    print("choice best backdoor by avg length: ", avg_best_index, acc_len)
    mb_next = get_unique_lists(merge_backdoors(acc, hards[i]))
    vars_mb_next = get_unique_literals(mb_next)
    len_mb_next = avg_length(mb_next)

    acc = get_unique_lists(merge_backdoors(acc, hards_to_merge[avg_best_index]))
    vars_merged = get_unique_literals(acc)
    len_merged = avg_length(acc)
    print("comprarison avg len: ", len_merged, len_mb_next)
    print("comprarison len: ", len(acc), len(mb_next))

    # erase merged backdoor
    hards_to_merge.pop(avg_best_index)
    print(len(hards_to_merge), "/", i + 1, "/", len(hards))

    prop_hit = 0

    # print(acc)
    time_to_merge = time.time() - time_merge
    print("Time to merge: ", time.time() - time_merge)
    filtered = []
    with Cadical153(bootstrap_with=formula) as solver:
        for j in range(len(acc)):
            # print(j, len(decart[i]))
            time_iter = time.time()
            solver.conf_budget(5000)
            # print(decart[i][j])
            solver.solve_limited(assumptions=acc[j])
            if solver.get_status() is None:
                filtered.append(acc[j])
            print("Time to iteration: ", time.time() - time_iter)
            print(len(filtered), "/", j + 1, "/", len(acc))
            print(solver.accum_stats())
    statistics = dict()
    # avg length of backdoor
    statistics['name'] = sys.argv[1]
    statistics['time_to_merge'] = round(time_to_merge, 3)
    statistics['new_vars'] = len(vars_merged - vars_acc)
    statistics['vars'] = len(vars_acc)
    statistics['length'] = avg_length(acc)
    statistics['var_mb_next'] = len(vars_mb_next)
    statistics['len_mb_next'] = len_mb_next
    statistics['prop_hit'] = prop_hit
    statistics['time'] = round(time.time() - start)
    statistics['iteration_time'] = round(time.time() - time_merge)
    statistics['iteration'] = i
    statistics['acc'] = len(acc)
    statistics['filtered'] = len(filtered)
    # format 2 digits after point sifted
    statistics['sifted'] = round((len(acc) - len(filtered)) / len(acc), 2)
    print("sifted: ", (len(acc) - len(filtered)) / len(acc), "filtered:", len(filtered), "acc:", len(acc))
    print("time from start: ", time.time() - start)
    acc = filtered
    if len(filtered) == 0:
        print("SUCCESS")
        statistics['success'] = True
        send_to_telegram(statistics, sys.argv[2])
        break
    send_to_telegram(statistics, sys.argv[2])

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
