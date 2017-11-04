import json
import sys

fname = sys.argv[1]

with open(fname) as f:
    r = json.load(f)

glist = []
for k, v in r.iteritems():
    cid, loop, mat_n, gflops, elapsed = v['msg'].split(" ",1)[0].split(":")[1].split(",")
    glist.append(float(gflops))

with open(fname + ".gflops", "w") as f:
    json.dump(glist, f, indent=4)
