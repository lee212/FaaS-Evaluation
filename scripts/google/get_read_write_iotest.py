import sys
import json
import numpy as np

fname = sys.argv[1]
ofname = sys.argv[2]

res = []
w = []
r = []
with open(fname) as f:
    rdict = json.load(f)
    for i in rdict:
        # Looking for 
        # "payload": "stdout: {'write': 23.941399812698364, 'read':
        #            1.6161670684814453}\nstderr: ",
        keystr = "stdout:"
        if i['payload'].find(keystr) == 0:
            stdout = i['payload'][len(keystr):].split("\n")[0]
            msg = json.loads(stdout.replace("'","\""))
            res.append([msg['read'], msg['write']])
            r.append(msg['read'])
            w.append(msg['write'])

print ("read mb/s: {}\nwrite mb/s: {}".format( 100 / np.mean(r),
    100 /np.mean(w)))

with open(ofname, "w") as f:
    json.dump(res, f, indent=4)
