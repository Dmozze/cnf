import numpy as np
from pysat.solvers import Cadical153

import utils


def work(list_to_sift, formula):
    inner_filtered = []
    solver = Cadical153(bootstrap_with=formula)
    cnt_steps = 0
    for j in range(len(list_to_sift)):
        cnt_steps += 1
        if cnt_steps >= utils.conf['sifter']['steps_before_restart']:
            solver.delete()
            solver = Cadical153(bootstrap_with=formula)
            cnt_steps = 0
        # time_iter = time.time()
        solver.conf_budget(utils.conf['sifter']['budget'])
        solver.solve_limited(assumptions=list_to_sift[j])
        if solver.get_status() is None:
            inner_filtered.append(list_to_sift[j])
        # print("Time to iteration: ", time.time() - time_iter)
        # print(len(inner_filtered), "/", j + 1, "/", len(list_to_sift))
        # print(solver.accum_stats())
    solver.delete()
    return inner_filtered


def set_up_threads(acc, threads_num, formula):
    acc_parts = np.array_split(acc, max(threads_num, len(acc) / 150))
    for j in range(len(acc_parts)):
        acc_parts[j] = acc_parts[j].tolist()

    # set up threads
    from multiprocessing import Pool

    # bind formula to work with
    from functools import partial

    work_up = partial(work, formula=formula)

    with Pool(threads_num) as pool:
        # add formula
        inner_results = pool.map(work_up, acc_parts)

    # merge results
    filtered = []
    for result in inner_results:
        filtered += result

    return filtered
