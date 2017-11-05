import json
import sys

def parse_event(msg):
    result = {}
    cut_length = 5
    mtype = msg[:cut_length]
    # [INFO]\t2017-10-30T05:39:31.221Z\ta8129aef-bd34-11e7-ac9
    # 2-6fc3e515585c\t1,1024,29.1802033036,0.383911\n"
    if mtype == "[INFO]"[:cut_length]:
        mmtype, mdate, mid, txt = msg.split("\t")
        result['id'] = mid
        txt = txt.strip()
        res = txt.split(",")
        # cid, loop, mat_n, gflops,func_elapsed, all_elapsed, init_numpy
        # 1684,1,1024,17.994209007,0.238927,0.238958, False
        if len(res) == 7:
            result['gflops'] = float(res[3])
            result['func_elapsed'] = float(res[4])
            result['all_elapsed'] = float(res[5])
            result['init_numpy'] = True if res[6] == "True" else False
    # REPORT RequestId: a8129aef-bd34-11e7-ac92-6fc3e515585c\t
    # Duration: 15982.64 ms\tBilled Duration: 16000 ms \tMemory Size: 1536 MB\tMax
    # Memory Used: 547 MB\t\n"
    elif mtype == "REPORT"[:cut_length]:
        mhead, duration, rest = msg.split("\t", 2)
        mid = mhead.split(": ")[1]
        mseconds = float(duration.split(": ")[1][:-3])
        result['mseconds'] = mseconds
        result['id'] = mid
    # Ignore other type of messages
    return result

fname = sys.argv[1]
with open(fname) as f:
    r = json.load(f)

rdict = {}
for i in r:
    mdict = parse_event(i['message'])
    if mdict:
        if not mdict['id'] in rdict:
            rdict[mdict['id']] = mdict
        else:
            rdict[mdict['id']].update(mdict)

cslist = []
tdlist = []
for k, v in rdict.iteritems():
    tdiff = 0
    try:
        tdiff = v['mseconds'] - (v['func_elapsed'] * 1000)
    except:
        continue
    if v['init_numpy']:
        cslist.append(tdiff)
    else:
        if tdiff > 100:
            print k, v
        tdlist.append(tdiff)

with open(fname + ".cslist", "w") as f:
    json.dump(cslist, f)
with open(fname + ".tdlist", "w") as f:
    json.dump(tdlist, f)
