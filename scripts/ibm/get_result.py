import json
import subprocess
import sys

fname = sys.argv[1]
with open(fname) as f:
    r = json.load(f)

keys = r.keys()
adict = {}
glist = []
for i in keys:
   res = subprocess.check_output("bx wsk activation result {}".format(i).split())
   rdict = json.loads(res)
   cid, loop, mat_n, gflops, elapsed = rdict['msg'].split(",")
   adict[cid] = gflops
   glist.append(gflops)

print len(adict)

with open(fname + ".result", "w") as f:
    json.dump(glist, f)
