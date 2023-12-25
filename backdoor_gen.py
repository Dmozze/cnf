import os
import time
import sys

base_setup = "./build/minisat {0} -ea-seed=42 -ea-num-runs={1} -ea-instance-size={2} -ea-num-iters={3} -ea-output-path={4} &"
cnf_string = "lec_mult_{0}_{1}x{1}.cnf"

cnfs_types = ['CvK'] #, 'CvD', 'CvW', 'DvK', 'DvW', 'KvW']
sizes = ['12'] #['10', '11', '12']

runs = 100
iterations = 5000
backdoor_sizes = ['7', '8', '9', '10', '11', '12']

gen = sys.argv[1] == "gen"

if gen:
    os.system("mkdir results")
    for muls in cnfs_types:
        for size in sizes:
            current_cnf = cnf_string.format(muls, size)
            current_cnf_name = muls + "_" + size
            # make dir for current cnf
            os.system("mkdir results/" + current_cnf_name)
            # copy cnf to results dir
            os.system("cp cnfs/" + current_cnf + " results/" + current_cnf_name + "/")
            os.system("mkdir results/" + current_cnf_name + "/backdoors")
            # save meta about generation
            meta = open("results/" + current_cnf_name + "/meta.txt", "w")
            meta.write("cnf: " + current_cnf + "\n")
            meta.write("runs: " + str(runs) + "\n")
            meta.write("iterations: " + str(iterations) + "\n")
            meta.write("backdoor_sizes: " + str(backdoor_sizes) + "\n")
            meta.close()
            for backdoor_size in backdoor_sizes:
                current_setup = base_setup.format("cnfs/" + current_cnf, runs, backdoor_size, iterations, "results/" + current_cnf_name + "/backdoors" + "/" + backdoor_size + ".txt")
                print(current_setup)
                os.system(current_setup)
            time.sleep(10)
    time.sleep(150)
# merge backdoors to one
for muls in cnfs_types:
    for size in sizes:
        current_cnf_name = muls + "_" + size
        for backdoor_size in backdoor_sizes:
            os.system("cat results/" + current_cnf_name + "/backdoors/" + backdoor_size + ".txt >> results/" + current_cnf_name + "/backdoors.txt")
        check_all_lines_copy = "cat results/" + current_cnf_name + "/backdoors.txt | wc -l"
        if os.system(check_all_lines_copy) != runs * len(backdoor_sizes):
            print("ERROR: " + current_cnf_name)
