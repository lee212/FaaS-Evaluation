import json
import sys

fname = sys.argv[1]
with open(fname) as f:
    r = json.load(f)

nres = {}
for k, v in r.iteritems():
    idx, rsize, ntry = k.split("_")
    nres[idx] = { "workload_size": rsize,
            "number_of_try": ntry,
            "response": v
            }

with open(fname + ".updated", "w") as f:
    json.dump(nres, f, indent=4)
