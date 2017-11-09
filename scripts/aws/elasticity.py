from random import randint
import invoke
import json
import os
import time
import sys
import time
import numpy as np

interval = 0.2
cold_start_delay = 0
bins_invoke = [[0, 50], [50, 100], [100, 200], [0, 200]]
rand_numbers = np.concatenate([np.random.randint(1, 4, size=50), \
        np.random.randint(3, 7, size=25), \
        np.random.randint(2, 6, size=25), \
        np.random.randint(6, 10, size=12), \
        np.random.randint(10, 14, size=13), \
        np.random.randint(14, 17, size=12), \
        np.random.randint(17, 20, size=13), \
        np.random.randint(20, 25, size=10), \
        np.random.randint(20, 30, size=15), \
        np.random.randint(35, 50, size=25), \
        np.random.randint(40, 55, size=25), \
        np.random.randint(20, 30, size=25), \
        np.random.randint(25, 35, size=25), \
        np.random.randint(35, 45, size=25), \
        np.random.randint(50, 65, size=25), \
        np.random.randint(40, 50, size=15), \
        np.random.randint(30, 40, size=15), \
        np.random.randint(25, 35, size=10), \
        np.random.randint(20, 30, size=10), \
        np.random.randint(15, 25, size=10), \
        np.random.randint(25, 35, size=10), \
        np.random.randint(35, 40, size=10), \
        np.random.randint(30, 35, size=10), \
        np.random.randint(25, 30, size=10), \
        np.random.randint(50, 60, size=10), \
        np.random.randint(59, 69, size=10), \
        np.random.randint(65, 79, size=10), \
        np.random.randint(75, 89, size=10), \
        np.random.randint(60, 90, size=10), \
        np.random.randint(70, 90, size=10), \
        np.random.randint(55, 70, size=25)])

func_name = "comp_1536_10"
loop = 10
mat_n = 1024

res = {}
idx = 0

if len(sys.argv) < 3:
    print "run_type func_name interval(sec)"
    sys.exit()

run_type = sys.argv[1]
func_name = sys.argv[2]
interval = float(sys.argv[3])

if run_type != "concurrent" and run_type != "sequential":
    run_type = "sequential"

print "{} is chosen".format(run_type)

for isize in rand_numbers:

    event = {"function_name":  func_name,
            "invoke_size": isize,
            "number_of_loop": loop,
            "number_of_matrix": mat_n }

    if run_type == "concurrent":
        ret = (invoke.handler(event))
        print "{} invoked and sleep {}".format(isize, interval)
        time.sleep(interval)
    else:
        ret = []
        for k in range(isize):
            argument = (func_name, k, loop, mat_n)
            ret.append(invoke.invoke(argument))
            time.sleep(interval)
    # Not saving 'Payload': <botocore.response.StreamingBody object at
    # 0x7f6a9ab62510>,
    for j in ret:
        del (j['Payload'])

    if idx == 0:
        print "cold start delay in {} seconds".format(cold_start_delay)
        time.sleep(cold_start_delay)
    key_name = "{}_{}".format(idx, isize)
    res[key_name] = ret
    idx += 1
   
with open(os.path.basename(__file__).split(".")[0] + func_name + ".log", "w") as f:
    json.dump(res, f)
