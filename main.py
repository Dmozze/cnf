from pysat.solvers import Cadical153
from pysat.formula import CNF
import sys
import time
import numpy as np
import pandas as pd
import seaborn as sns
import bi

from utils.backdoors import calculate_quality_of_backdoor
from utils.sifter import set_up_threads, work
from utils.telegram import send_to_telegram, send_to_photo
from utils.backdoors import get_all_units_from_backdoor, get_all_biunits_from_backdoor

formula_path = 'original.cnf'
backdoor_path = 'backdoors.txt'
hist_path = 'hist.png'
iteration_plot_path = 'output.png'
solved = True

if __name__ == '__main__':
    start = time.time()

    prop_hit = 0


    def backdoor_string_to_list(backdoor_string):
        return list(map(lambda x: x + 0, map(int, backdoor_string.split('[')[1].split(']')[0].split(', '))))


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
        (status, literals) = base_solver.propagate(assumptions)

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
        # print(cnt, len(results))
        results = list(filter(lambda x: x[0] is None, results))
        # print(cnt, len(results))
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
    send_to_telegram(statistics)

    # histogram of backdoors length
    hards_in_backdoors = []
    for i in range(len(decart)):
        hards_in_backdoors.append(len(decart[i]))

    sns_plot = sns.histplot(hards_in_backdoors, kde=True).set_title(sys.argv[1])
    sns_plot.figure.savefig(hist_path)

    sns_plot.figure.clf()

    send_to_photo(hist_path)


    solving_times = {}

    LIMITED_SOLVED = "LIMITED_SOLVED"
    FULL_SOLVED = "FULL_SOLVED"
    LIMITED_SOLVED_ACC = "LIMITED_SOLVED_ACC"
    FULL_SOLVED_ACC = "FULL_SOLVED_ACC"

    solving_times[LIMITED_SOLVED] = []
    solving_times[FULL_SOLVED] = []
    solving_times[LIMITED_SOLVED_ACC] = []
    solving_times[FULL_SOLVED_ACC] = []


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
        send_to_telegram(statistics)
        if all_one_hard:
            for i in range(len(all_one_hard)):
                base_solver.add_clause([all_one_hard[i]])
                formula.append([all_one_hard[i]])
        else:
            print("UNSAT")
            exit()

    print("len" + str(len(one_hard)))
    print("FORMULA LENGTH: ", len(formula.clauses))
    hards = list(filter(lambda x: len(x) > 1, decart))
    hards.sort(key=lambda x: len(x))
    statistics = dict()
    statistics['name'] = sys.argv[1]
    statistics['hards_length'] = len(hards)
    flat_list = [item for sublist in hards for item in sublist]
    kek = [item for sublist in flat_list for item in sublist]
    statistics['hards_vars'] = len(hards)
    send_to_telegram(statistics)
    statistics = dict()

    # print(calculate_quality_of_backdoor(hards))

    # print(list(map(len, decart)))
    hards_to_merge = hards.copy()
    hards_to_merge.pop(0)
    acc = hards[0]
    threads_num = 8
    inserted_units = set()
    for i in range(1, len(hards)):
        time_merge = time.time()
        prop_hit = 0
        acc = get_unique_lists(merge_backdoors(acc, hards[i]))
        # print(acc)
        unit = get_all_units_from_backdoor(acc)
        # print(unit)
        for j in range(len(unit)):
            if abs(unit[j]) not in inserted_units:
                formula.append([-unit[j]])
                inserted_units.add(abs(unit[j]))
        print("HARDS")
        for j in range(len(acc)):
            acc[j].sort(key=lambda x: abs(x))
        for j in range(len(acc)):
            print(acc[j])
        print("HARDS")
        bi_units = get_all_biunits_from_backdoor(acc)
        cnfs = bi.all_sets_of_clauses(2)
        mapb = bi.get_map_to_dnf()
        # print("INSERTED:", inserted_units)
        print("ACC: ", len(acc))

        # for biunit in bi_units.values():
        #     bis = list(biunit)
        #     if len(bis) == 4 or len(bis) == 1:
        #         continue
        #
        #     var_a = abs(bis[0][0])
        #     var_b = abs(bis[0][1])
        #     if var_a > var_b:
        #         var_a, var_b = var_b, var_a
        #     key = (var_a, var_b)
        #     if var_a in inserted_units or var_b in inserted_units:
        #         continue
        #     assert len(bis) == 2 or len(bis) == 3
            # maybe = bi.map_values_from_cnf(var_a, var_b, bis)
            # jj = bi.all_clauses(2)
            # diff = []
            # for j in range(len(jj)):
            #     if jj[j] not in maybe:
            #         diff.append(jj[j])

            # diff = bi.map_values_to_cnf(var_a, var_b, diff)
            # print(bis)
            # if len(bis) == 3:
            #     diff = [-diff[0][0], -diff[0][1]]
            #     print("DIFF3", diff)
            #     if key not in inserted_units:
            #         formula.append(diff)
            #         inserted_units.add(key)
            # if len(bis) == 2:
            #     print("DIFF2", diff)
            #     if key not in inserted_units:
            #         inserted_units.add(key)
            #         formula.append(diff[0])
            #         formula.append(diff[1])

            # print(">>>>>>>>")
            # print(bis)
            # print(diff)
            # print("=============")
            # print(bis)
            # mapped = bi.map_values_from_cnf(var_a, var_b, bis)
            # id_in_cnfs = -1
            # mapped.sort()
            # for i in range(len(cnfs)):
            #     cnfs[i].sort()
            #     if cnfs[i] == mapped:
            #         id_in_cnfs = i
            #         break
            # direct_cnf = cnfs[mapb[id_in_cnfs]]
            # print(direct_cnf)
            # direct_cnf = bi.map_values_to_cnf(var_a, var_b, direct_cnf)
            # print(direct_cnf)
            # print("=============")
            # for j in range(len(direct_cnf)):
            #     hash = direct_cnf[j][0] * 1000000 + direct_cnf[j][1]
            #     if hash not in inserted_units:
            #         formula.append(direct_cnf[j])
            #         inserted_units.add(hash)
            #         print(direct_cnf[j])
            # print("<<<<<<<<")

        # print("Units: ", len(unit), "Biunits: ", len(biunit))
        print("Formula length: ", len(formula.clauses))
        # formula.append(unit)

        product_size_before_prop.append(len(acc) + prop_hit)
        product_size_after_prop.append(len(acc))

        # print(acc)
        time_to_merge = time.time() - time_merge
        print("Time to merge: ", time.time() - time_merge)

        # track time to full solving
        time_full = time.time()

        filtered = set_up_threads(acc, threads_num, formula)

        time_full = time.time() - time_full


        # track time to limited solving
        time_limited = time.time()

        if len(acc) < threads_num * 40 or threads_num == 1:
            filtered = work(acc, formula)
        else:
            filtered = set_up_threads(acc, threads_num, formula)

        time_limited = time.time() - time_limited

        solving_times[LIMITED_SOLVED_ACC].append(solving_times[LIMITED_SOLVED_ACC][-1] + time_limited)
        solving_times[FULL_SOLVED_ACC].append(solving_times[FULL_SOLVED_ACC][-1] + time_full)
        solving_times[LIMITED_SOLVED].append(time_limited)
        solving_times[FULL_SOLVED].append(time_full)


        def get_statistics():
            inner_statistics = dict()
            inner_statistics['name'] = sys.argv[1]
            inner_statistics['time_to_merge'] = round(time_to_merge, 3)
            inner_statistics['length'] = avg_length(acc)
            inner_statistics['prop_hit'] = prop_hit
            inner_statistics['time'] = round(time.time() - start)
            inner_statistics['iteration_time'] = round(time.time() - time_merge)
            inner_statistics['iteration'] = i
            inner_statistics['acc'] = len(acc)
            inner_statistics['filtered'] = len(filtered)
            inner_statistics['sifted'] = round((len(acc) - len(filtered)) / len(acc), 2)
            inner_statistics['all_sifted'] = round((len(acc) - len(filtered)) / (prop_hit + len(acc)), 2)
            if len(filtered) == 0:
                global solved
                solved = True
                inner_statistics[LIMITED_SOLVED_ACC] = solving_times[LIMITED_SOLVED_ACC]
                inner_statistics[FULL_SOLVED_ACC] = solving_times[FULL_SOLVED_ACC]
                print("SUCCESS")
                inner_statistics['success'] = True
            return inner_statistics


        print("sifted: ", (len(acc) - len(filtered)) / len(acc), "filtered:", len(filtered), "acc:", len(acc))
        print("time from start: ", time.time() - start)
        product_size_after_sifting.append(len(filtered))
        if len(filtered) == 0:
            send_to_telegram(get_statistics())
            break
        send_to_telegram(get_statistics())
        acc = filtered

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

    sns_plot.figure.savefig(iteration_plot_path)

    send_to_photo(iteration_plot_path)

    if not solved:
        for i in range(len(acc)):
            base_solver.solve(assumptions=acc[i])
            print(base_solver.get_status())

    print("Time: ", time.time() - start)
