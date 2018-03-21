import json
import sys

fname = sys.argv[1]
ofname = sys.argv[2]
res = []
with open(fname) as f:
    r = json.load(f)

    for k, v in r.items():
        try:
            duration = v["duration"]
            res.append(duration * 0.001)
        except:
            print (v)
            continue

#res.sort()

with open(ofname, "w") as f:
    json.dump(res, f, indent=4)
