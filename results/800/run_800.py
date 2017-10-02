from multiprocessing.pool import ThreadPool
import urllib
import time
from pprint import pprint as pp
import json
import requests

tp = ThreadPool(800)

loop = 1
matrix = 512

start=1100
end=1900

def worker(n):
    url = "https://flops{0}.azurewebsites.net/api/HttpTriggerPythonGFlops".format(n)
    payload = {"number_of_loop": loop, "number_of_matrix": matrix}
    s = time.time()
    r = requests.post(url,data=json.dumps(payload))
    e = time.time() - s
    res = r.text
    return (n, res, e)

res = {}

def collect(n):
    res[n[0]] = {
            'result': n[1],
            'elapsed_time': n[2]}

cblist = [] 
for i in range(start, end):

    cb = tp.apply_async(worker, (i,))
    cblist.append(cb)

for i in cblist:
    n = i.get()
    res[n[0]] = {
            'result': n[1],
            'elapsed_time': n[2]}

pp (res)
with open("run_800.result","wb") as fout:
    json.dump(res, fout, indent=2)

