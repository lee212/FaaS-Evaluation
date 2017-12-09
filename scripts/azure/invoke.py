from multiprocessing.pool import ThreadPool, TimeoutError
from urlparse import urlparse
import urllib
import time
from pprint import pprint as pp
import json
import requests
import sys
import os

thread_num = 64
timeout_sec=60
res = {}

def worker(n):
    cid, url, payload = n
    #url = "https://flops{0}.azurewebsites.net/api/HttpTriggerPythonGFlops".format(n)
    #payload = {"number_of_loop": loop, "number_of_matrix": matrix}
    s = time.time()
    try:
        r = requests.post(url,data=json.dumps(payload), timeout=timeout_sec,
                headers = {'content-type': 'application/json'})
        ret = r.text
    except requests.exceptions.ReadTimeout as e:
        ret = unicode(e, 'utf-8')
    e = time.time() - s
    return (cid, ret, e)

def collect(n):
    res[n[0]] = {
            'result': n[1],
            'elapsed_time': n[2]}

if __name__ == "__main__":

    if len(sys.argv) < 5:
        print "cnt url params concurrent|sequential start end timout_second"
        sys.exit(-1)

    cnt = int(sys.argv[1])
    url = sys.argv[2]
    params = json.loads(sys.argv[3])
    parallel = True if sys.argv[4] == "concurrent" else False
    # optional
    if len(sys.argv) > 5:
        start = int(sys.argv[5])
        end = int(sys.argv[6])
    else:
        start = 0
        end = cnt
    if len(sys.argv) == 8:
        timeout_sec = int(sys.argv[7])

    tp = ThreadPool(thread_num)
    
    cblist = [] 
    for cid in range(start, end):

        arguments = (cid, url, params)
        if parallel:
            cblist.append(tp.apply_async(worker, (arguments,)))
        else:
            cblist.append(worker(arguments))

    for i in cblist:
        if parallel:
            try:
                n = i.get(timeout_sec)
            except TimeoutError:
                n = (start, None, None)
            except:
                n = (start, None, None)
        else:
            n = i
        res[n[0]] = {
                'result': n[1],
                'elapsed_time': n[2]}
        start += 1

    tp.close()
    tp.join()

    params_str = ''.join(e for e in str(params) if e.isalnum() or e == ":")
    url_str = urlparse(url).hostname.split(".")[0]
    with open("{}.{}.{}.{}.log".format(os.path.basename(__file__).split(".")[0],
        cnt, url_str, params_str),"wb") as fout:
            json.dump(res, fout, indent=2)

