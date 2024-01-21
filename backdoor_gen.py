import os
import random
import time
import sys
import subprocess

def flatten(l):
    return [item for sublist in l for item in sublist]


base_setup = "./build/minisat {0} -ea-seed=42 -ea-num-runs={1} -ea-instance-size={2} -ea-num-iters={3} -ea-output-path={4} -ea-bans={5} &"
cnf_string = "lec_mult_{0}_{1}x{1}.cnf"

cnfs_types = ['CvK']  # , 'CvD', 'CvW', 'DvK', 'DvW', 'KvW']
sizes = ['12']  # ['10', '11', '12']

runs = 1
meta_runs = 100
iterations = 15000
backdoor_sizes = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16']

gen = sys.argv[1] == "gen"

temp_file = "temp.txt"
current_backdoors = []
if gen:
    os.system("mkdir results")
    for muls in cnfs_types:
        for size in sizes:
            for meta in range(meta_runs):
                flatten_backdoors = flatten(current_backdoors)
                if len(flatten_backdoors) != len(set(flatten_backdoors)):
                    print("ERROR: " + muls + "_" + size)
                    print(len(flatten_backdoors))
                    print(len(set(flatten_backdoors)))
                    assert False
                current_cnf = cnf_string.format(muls, size)
                current_cnf_name = muls + "_" + size
                # make dir for current cnf
                os.system("mkdir results/" + current_cnf_name)
                # copy cnf to results dir
                os.system("cp cnfs/" + current_cnf + " results/" + current_cnf_name + "/")
                os.system("mkdir results/" + current_cnf_name + "/backdoors")

                # remove temp file
                os.system("rm " + temp_file)
                random.shuffle(backdoor_sizes)
                get_random_backdoor_size = backdoor_sizes[0]
                # save meta about generation
                # meta = open("results/" + current_cnf_name + "/meta.txt", "w")
                # meta.write("cnf: " + current_cnf + "\n")
                # meta.write("runs: " + str(runs) + "\n")
                # meta.write("iterations: " + str(iterations) + "\n")
                # meta.write("backdoor_sizes: " + str(backdoor_sizes) + "\n")
                # meta.close()
                current_setup = base_setup.format("cnfs/" + current_cnf, runs, get_random_backdoor_size, iterations,
                                                  temp_file, ",".join(flatten_backdoors))
                print("current_setup:", current_setup)
                os.system(current_setup)
                # get size of temp file
                temp_file_size = "cat " + temp_file + " | wc -l"
                while int(subprocess.check_output(temp_file_size, shell=True)) != runs:
                    print("wait")
                    time.sleep(1)
                print("ok file")
                # parse temp file
                with open(temp_file, 'r') as f:
                    for line in f:
                        current_backdoors.append(line.split(':')[1].strip(' \n][').split(', '))
                print("current_backdoors:", current_backdoors)

# save backdoors to backdoors.txt

with open("backdoors.txt", 'w') as f:
    for backdoor in current_backdoors:
        f.write(": " + str(backdoor) + "\n")


# merge backdoors to one
# for muls in cnfs_types:
#     for size in sizes:
#         current_cnf_name = muls + "_" + size
#         for backdoor_size in backdoor_sizes:
#             os.system("cat results/" + current_cnf_name + "/backdoors/" + backdoor_size + ".txt >> results/" + current_cnf_name + "/backdoors.txt")
#         check_all_lines_copy = "cat results/" + current_cnf_name + "/backdoors.txt | wc -l"
#         if os.system(check_all_lines_copy) != runs * len(backdoor_sizes):
#             print("ERROR: " + current_cnf_name)
