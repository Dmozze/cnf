from pysat.solvers import Cadical153
from pysat.formula import CNF
import sys
import time
import numpy as np
import pandas as pd
import seaborn as sns

from telegram import send_to_telegram, send_to_photo

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


def avg_length(arg):
    return sum(map(len, arg)) / len(arg)


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

# seaborn set up
product_size_before_prop = []
product_size_after_prop = []
product_size_after_sifting = []
product_len = []

statistics = dict()
statistics['name'] = sys.argv[1]
statistics['time_to_load'] = round(time.time() - start)
send_to_telegram(statistics, sys.argv[2])

# histogram of backdoors length
hards_in_backdoors = []
for i in range(len(decart)):
    hards_in_backdoors.append(len(decart[i]))

sns_plot = sns.histplot(hards_in_backdoors, kde=True).set_title(sys.argv[1])
sns_plot.figure.savefig("hist.png")

send_to_photo("hist.png")

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
    time_merge = time.time()
    prop_hit = 0
    acc = get_unique_lists(merge_backdoors(acc, hards[i]))
    product_size_before_prop.append(len(acc) + prop_hit)
    product_size_after_prop.append(len(acc))

    # print(acc)
    time_to_merge = time.time() - time_merge
    print("Time to merge: ", time.time() - time_merge)
    filtered = []
    with Cadical153(bootstrap_with=formula) as solver:
        for j in range(len(acc)):
            # print(j, len(decart[i]))
            time_iter = time.time()
            solver.conf_budget(40000)
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
    statistics['length'] = avg_length(acc)
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
    product_size_after_sifting.append(len(filtered))
    if len(filtered) == 0:
        print("SUCCESS")
        statistics['success'] = True
        send_to_telegram(statistics, sys.argv[2])
        break
    send_to_telegram(statistics, sys.argv[2])

iteration_num = len(product_size_after_prop)
iterations = list(range(iteration_num))
data_preproc = pd.DataFrame({
    'Iterations': iterations,
    'before propagation': np.array(product_size_before_prop),
    'after propagation': np.array(product_size_after_prop),
    'after sifting': np.array(product_size_after_sifting),
})


sns_plot = sns.lineplot(x='Iterations', y='value', hue='variable',
                        data=pd.melt(data_preproc, ['Iterations'])).set_title(sys.argv[1])

sns_plot.figure.savefig("output.png")

send_to_photo("output.png")

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
