from multiprocessing.pool import ThreadPool, TimeoutError
import urllib
import time
from pprint import pprint as pp
import json
import requests
import sys

num = 100
start = 1100
end = 1900
loop = 1
matrix = 512

timeout_sec=60
res = {}

def worker(n):
    url = "https://flops{0}.azurewebsites.net/api/HttpTriggerPythonGFlops".format(n)
    payload = {"number_of_loop": loop, "number_of_matrix": matrix}
    s = time.time()
    try:
        r = requests.post(url,data=json.dumps(payload), timeout=timeout_sec)
        res = r.text
    except requests.exceptions.ReadTimeout as e:
        res = unicode(e, 'utf-8')
    e = time.time() - s
    return (n, res, e)

def collect(n):
    res[n[0]] = {
            'result': n[1],
            'elapsed_time': n[2]}

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        num = int(sys.argv[1])
    if len(sys.argv) >= 3:
        start = int(sys.argv[2])
        end = int(sys.argv[3])
    if len(sys.argv) >= 5:
        loop = int(sys.argv[4])
        matrix = int(sys.argv[5])
    if len(sys.argv) == 7:
        timeout_sec = int(sys.argv[6])

    tp = ThreadPool(num)
    
    cblist = [] 
    for i in range(start, end):

        cb = tp.apply_async(worker, (i,))
        cblist.append(cb)

    cnt = start
    for i in cblist:
        try:
            n = i.get(timeout_sec)
        except TimeoutError:
            n = (cnt, None, None)
        except:
            n = (cnt, None, None)

        res[n[0]] = {
                'result': n[1],
                'elapsed_time': n[2]}
        cnt += 1

    tp.close()
    tp.join()
    pp (res)
    with open("invoke_{0}_{1}_{2}_{3}_{4}.result".format(num, start, end, loop,
        matrix),"wb") as fout:
        json.dump(res, fout, indent=2)

