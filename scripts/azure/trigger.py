import requests
from multiprocessing.pool import ThreadPool
from datetime import datetime as dt
import json
import sys
import base64

def invoke(params):
    url, param = params
    r = requests.post(url, data=param,
    headers={"Content-Type":"application/json"})
    return r.text

def invoker(cnt, url, param):
    p = ThreadPool(64)
    res = []
    stime = dt.now()
    argument = (url, param)
    for i in range(int(cnt)):
        res.append(p.apply_async(invoke, args=(argument,)))
    itime = dt.now()

    nres = {}
    cnt = 0
    for i in res:
        nres[cnt] = i.get()
        cnt+=1

    etime = dt.now()
    p.close()
    p.join()
    print "{},{},{}".format(itime - stime, etime - itime, etime - stime)
    return nres

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "cnt url param"
        sys.exit()
    cnt = sys.argv[1]
    url = sys.argv[2]
    param = sys.argv[3]
    r = invoker(cnt, url, param)
    url_base64 = base64.b64encode(url)
    with open("trigger.{}.{}.{}.result".format(cnt,
    url_base64,base64.b64encode(param)),"w") as f:
        json.dump(r, f)

