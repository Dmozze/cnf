def calculate_quality_on_prefix(backdoors, prefix):
    # calc length of prefix
    backdoors = backdoors[:prefix]
    length = sum([len(backdoor) for backdoor in backdoors])
    return length / len(backdoors)


def calculate_quality_of_backdoor(backdoors):
    length = len(backdoors)
    p10 = int(length * 0.1)
    p25 = int(length * 0.25)
    p50 = int(length * 0.5)
    p75 = int(length * 0.75)
    p90 = int(length * 0.9)
    p100 = int(length * 1)
    qualities = [p10, p25, p50, p75, p90, p100]
    return list(map(lambda x: calculate_quality_on_prefix(backdoors, x), qualities))


def get_all_units_from_backdoor(hard_tasks):
    if len(hard_tasks) == 0:
        return []
    units = set()
    for unit in hard_tasks[0]:
        units.add(unit)
        units.add(-unit)
    for hard_task in hard_tasks:
        for unit in hard_task:
            if unit in units:
                units.remove(unit)
    return list(units)


def get_all_biunits_from_backdoor(hard_tasks):
    if len(hard_tasks) == 0:
        return []
    units = dict()
    # for unit_i in range(len(hard_tasks[0])):
    #     for unit_j in range(unit_i + 1, len(hard_tasks[0])):
    #         unit_a = hard_tasks[0][unit_i]
    #         unit_b = hard_tasks[0][unit_j]
    #         if abs(unit_a) > abs(unit_b):
    #             unit_a, unit_b = unit_b, unit_a
    #         key = (abs(unit_a), abs(unit_b))
    #         if key not in units:
    #             units[key] = set()
    #             units[key].add((unit_a, unit_b))
    #             units[key].add((-unit_a, unit_b))
    #             units[key].add((unit_a, -unit_b))
    #             units[key].add((-unit_a, -unit_b))

    for hard_task in hard_tasks:
        for unit_i in range(len(hard_task)):
            for unit_j in range(unit_i + 1, len(hard_task)):
                unit_a = hard_task[unit_i]
                unit_b = hard_task[unit_j]
                if abs(unit_a) > abs(unit_b):
                    unit_a, unit_b = unit_b, unit_a
                key = (abs(unit_a), abs(unit_b))
                if key not in units:
                    units[key] = set()
                units[key].add((unit_a, unit_b))
    return units
