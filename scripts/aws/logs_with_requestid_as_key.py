import json
import sys
import re

fnames = sys.argv[1]

ar = {}
err = []
for fname in fnames.split(","):
    with open(fname) as f:
        r = json.load(f)

    for i in r:
        t = \
        re.match(".*([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}).*",
                i['message'])
        try:
            key = t.group(1)
        except:
            err.append(i)
            continue
        if key in ar:
            ar[key].append(i)
        else:
            ar[key] = [i]
        '''
        if i['message'].find('1024') > 0:
            try:
                # 21,10,1024,17.4369022563,1.314976,1.315003,False
                cid, loop, mat_n, gflop, func_elapsed, all_elapsed, init_numpy = i['message'].split("\t")[3].split(",")
            except:
                pass
            ar[key] = {"cid": cid,
                    "loop": loop,
                    "mat_n": mat_n,
                    "gflop": gflop,
                    "func_elapsed": func_elapsed,
                    "all_elapsed": all_elapsed,
                    "init_numpy": init_numpy,
                    "timestamp": i['timestamp'],
                    "raw": i['message']
                    }
        '''

with open(fname +  ".elastic", "w") as f:
    json.dump(ar, f, indent=4)

with open(fname +  ".elastic.err", "w") as f:
    json.dump(err, f, indent=4)


