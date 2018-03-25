import sys
import json

fname = sys.argv[1]
ofname = sys.argv[2]
with open(fname) as f:
    r = json.load(f)

res = []
err = []
for k, v in r.items():
    try:
        msgd = json.loads(v[1]['payload'])
        seqid =  msgd['function_results']['params']['seqid']
        cid =  msgd['function_results']['params']['cid']
        elapsed =  msgd['function_results']['elapsed_second']
        init =  msgd['host_info']['init']
    except json.decoder.JSONDecodeError as e:
        #  "payload": "Function execution took xxx ms,
        #  finished with status: 'connection error'",
        err.append(v[1]['payload'])
        continue
    except:
        continue
    res.append([seqid, cid, elapsed, init])

print (len(err))
res = sorted(res, key = lambda x: (x[0], x[1]))
seqid = 1
cid = 0
nres = []
errcnt = 0
idx = 0
while seqid < 51:
#for i in res:
    i = res[idx]
    if i[0] == seqid and i[1] == cid:
        nres.append(i)
        idx += 1
    else:
        print (i, seqid, cid)
        nres.append([seqid, cid, 0, True])
        errcnt += 1
    cid += 1
    if  cid % 10 == 0:
        seqid += 1
        cid = 0

print (errcnt)
with open(ofname, "w") as f:
    json.dump(nres, f, indent=4)
