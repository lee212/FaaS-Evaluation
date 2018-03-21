import sys
import json
fname = sys.argv[1]
ofname = sys.argv[2]
fstr = "Duration="

res = []
with open(fname) as f:
    for i in f.readlines():
        loc = i.find(fstr)
        if loc > 0:
            duration = i[loc + len(fstr):].split('m')[0]
            res.append(int(duration) * 0.001)

with open(ofname, "w") as f:
    json.dump(res, f, indent=4)

