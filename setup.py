import os
from datetime import datetime

from telegram import send_to_telegram

cnfs_types = ['CvK']  # , 'CvD', 'CvW', 'DvK', 'DvW', 'KvW']
sizes = ['10', '11', '12']

dumpy = "python3 dumpy.py {0} false > {1}"
main = "python3 main.py {0} false > {1}"
main_prev = "python3 prev_main.py {0} false > {1}"

# create logs dir if not exists
os.system("mkdir logs")
for muls in cnfs_types:
    for size in sizes:
        current_date_and_time = datetime.now()
        current_time_without_mills = str(current_date_and_time).split(".")[0]
        current_time_without_mills = current_time_without_mills.replace(" ", "_")

        try:
            os.system("mkdir logs/" + muls + "_" + size)
            os.system("mkdir logs/" + muls + "_" + size + "/" + current_time_without_mills)
            current_cnf = "results/" + muls + "_" + size + "/lec_mult_" + muls + "_" + size + "x" + size + ".cnf"
            current_cnf_name = muls + "_" + size

            # copy backdoors to backdoors.txt
            os.system("cp results/" + current_cnf_name + "/backdoors.txt backdoors.txt")

            # copy cnf to original.cnf
            os.system("cp " + current_cnf + " original.cnf")


            log_name_with_minutes = "logs/" + muls + "_" + size + "/" + current_time_without_mills + "/" + "main_prev.txt"
            os.system(main_prev.format("prev_" + current_cnf_name, log_name_with_minutes))

            # run main.py with time
            log_name_with_minutes = "logs/" + muls + "_" + size + "/" + current_time_without_mills + "/" + "main.txt"
            os.system(main.format("main_" + current_cnf_name, log_name_with_minutes))

            # run dumpy.py

            log_name_with_minutes = "logs/" + muls + "_" + size + "/" + current_time_without_mills + "/" + "dumpy.txt"
            os.system(dumpy.format("dumpy_" + current_cnf_name, log_name_with_minutes))
        except:
            send_to_telegram("ERROR: " + muls + "_" + size + " " + current_time_without_mills, "true")
