import sys
import json

fname = sys.argv[1]
ofname = sys.argv[2]

res = []
with open(fname) as f:
    r = json.load(f)
    for i in r:
        # Looking for 
        #         "payload": "Function execution took 3287 ms, finished with
        keystr = "Function execution took "
        if i['payload'].find(keystr) == 0:
            duration = i['payload'][len(keystr):].split()[0]
            # milliseconds to seconds
            res.append(int(duration)*0.001)

with open(ofname, "w") as f:
    json.dump(res, f, indent=4)
