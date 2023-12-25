import numpy as np
from pysat.solvers import Cadical153


def work(list_to_sift, formula):
    inner_filtered = []
    solver = Cadical153(bootstrap_with=formula)
    cnt_steps = 0
    for j in range(len(list_to_sift)):
        cnt_steps += 1
        if cnt_steps > 150:
            solver.delete()
            solver = Cadical153(bootstrap_with=formula)
            cnt_steps = 0
        # time_iter = time.time()
        solver.conf_budget(10000)
        solver.solve_limited(assumptions=list_to_sift[j])
        if solver.get_status() is None:
            inner_filtered.append(list_to_sift[j])
        # print("Time to iteration: ", time.time() - time_iter)
        # print(len(inner_filtered), "/", j + 1, "/", len(list_to_sift))
        # print(solver.accum_stats())
    solver.delete()
    return inner_filtered


# random shuffle acc
# np.random.shuffle(acc)

# split acc to threads_num parts


def set_up_threads(acc, threads_num, formula):
    acc_parts = np.array_split(acc, threads_num * 2)
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
