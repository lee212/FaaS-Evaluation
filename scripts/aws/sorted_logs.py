import sys
import json

fname = sys.argv[1]
ofname = sys.argv[2]
with open (fname) as f:
    r = json.load(f)

res = []
for k, v in r.items():
    # DATE\tMessageID\tRETURN
    try:
        msg = v[1]['message'].split("\t")[2] 
        msgd = json.loads(msg)
        seqid = msgd['function_results']['params']['seqid']
        cid = msgd['function_results']['params']['cid']
        elapsed = msgd['function_results']['elapsed_second']
        init = msgd['host_info']['init']
        gtrm = msgd['client_info']['getRemainingTimeInMillis']
        mlm = msgd['client_info']['memoryLimitInMB']
        ver = msgd['client_info']['version']
    except:
        continue
    res.append([seqid, cid, elapsed, init, gtrm, mlm, ver])

# Sort by seqid and cid
res = sorted(res, key = lambda x: (x[0], x[1]))
with open(ofname, "w") as f:
    json.dump(res, f, indent=4)
