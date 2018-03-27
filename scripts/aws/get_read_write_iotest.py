import json
import sys
import math
import numpy as np

if len(sys.argv) < 3:
    print ("log_filename output_filename result_filename")
    sys.exit()

log_fname = sys.argv[1]
ofname = sys.argv[2]

res_r = []

with open(log_fname) as f:
    log_r = json.load(f)

msec = 0
res = []
r = []
w = []
for i in log_r:
    if i['message'][0] == "{":
        msg = json.loads(i['message'].replace("'","\""))
        read = msg['read']
        write = msg['write']
        res.append([read, write])
        r.append(read)
        w.append(write)

print ("read mb/s: {}\nwrite mb/s: {}".format(100 / np.mean(r), 
    100 / np.mean(w)))

if res:
    with open(ofname, "w") as f:
        json.dump(res, f, indent=4)
