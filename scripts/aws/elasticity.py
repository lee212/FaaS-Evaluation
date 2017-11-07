from random import randint
import invoke
import json
import os
import time

interval = 0.1
cold_start_delay = 15
try_size = 150
bins_invoke = [[0, 50], [50, 100], [100, 200], [0, 200]]
func_name = "comp_1536_4"
loop = 10
mat_n = 1024

res = {}
idx = 0

for bini in bins_invoke:
    for i in range(try_size):
        isize = randint(bini[0], bini[1])

        event = {"function_name":  func_name,
                "invoke_size": isize,
                "number_of_loop": loop,
                "number_of_matrix": mat_n }

        ret = (invoke.handler(event))
        # Not saving 'Payload': <botocore.response.StreamingBody object at
        # 0x7f6a9ab62510>,
        for j in ret:
            del (j['Payload'])

        print "{} invoked and sleep {}".format(isize, interval)
        time.sleep(interval)
        if idx == 0:
            print "cold start delay in {} seconds".format(cold_start_delay)
            time.sleep(cold_start_delay)
        key_name = "{}_{}_{}".format(idx, isize, i)
        res[key_name] = ret
        idx += 1
    print "{},{} bin size completed".format(bini[0], bini[1])
   
with open(os.path.basename(__file__) + ".log", "w") as f:
    json.dump(res, f)
