import json
import sys

fname = sys.argv[1]

with open(fname) as f:
    r = json.load(f)
    rdict = {}
    for i in r:
        eid = i['labels']['execution_id']
        if eid in rdict:
            rdict[eid].append(i)
        else:
            rdict[eid] = [i]

with open("{}.eid".format(fname), "w") as f:
    json.dump(rdict, f, indent=4)
