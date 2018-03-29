import json
import sys
import numpy as np

fname = sys.argv[1]
ofname = sys.argv[2]
res = []
r = []
w = []

with open(fname) as f:
    rdict = json.load(f)
    for k, v in rdict.items():
        try:
            response = json.loads(v['result'])
            res.append([response['read'], response['write']])
            r.append(response['read'])
            w.append(response['write'])
        except:
            print (v)
            continue

print ("read mb/s:{}\nwrite mb/s:{}".format( 100 / np.mean(r),
    100 / np.mean(w)))

with open(ofname, "w") as f:
    json.dump(res, f, indent=4)
