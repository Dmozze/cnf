import os
from datetime import datetime

cnfs_types = ['CvK'] # , 'CvD', 'CvW', 'DvK', 'DvW', 'KvW']
sizes = ['10', '11', '12']

dumpy = "python3 dumpy.py {0} true > {1}"
main = "python3 main.py {0} true > {1}"

# create logs dir if not exists
os.system("mkdir logs")
for muls in cnfs_types:
    for size in sizes:

        current_date_and_time = datetime.now()
        current_time_without_mills = str(current_date_and_time).split(".")[0]
        current_time_without_mills = current_time_without_mills.replace(" ", "_")

        os.system("mkdir logs/" + muls + "_" + size)
        os.system("mkdir logs/" + muls + "_" + size + "/" + current_time_without_mills)
        current_cnf = "results/" + muls + "_" + size + "/lec_mult_" + muls + "_" + size + "x" + size + ".cnf"
        current_cnf_name = muls + "_" + size

        # copy backdoors to backdoors.txt
        os.system("cp results/" + current_cnf_name + "/backdoors.txt backdoors.txt")

        # copy cnf to original.cnf
        os.system("cp " + current_cnf + " original.cnf")


        # run main.py with time
        log_name_with_minutes = "logs/" + muls + "_" + size + "/" + current_time_without_mills + "/" + "main.txt"
        os.system(main.format(current_cnf_name, log_name_with_minutes))

        # run dumpy.py

        log_name_with_minutes = "logs/" + muls + "_" + size + "/" + current_time_without_mills + "/" + "dumpy.txt"
        os.system(dumpy.format(current_cnf_name, log_name_with_minutes))

