import copy
import json
import invoke
import base64
from google.cloud import storage
from multiprocessing.pool import ThreadPool

trigger_bucket_name = "bigdata-aggregate-reducer-trigger-lee212"
ibucket_name = obucket_name = "bigdata-lee212"
prefix = "aggregate.reduce/"
okey = "aggregate.result/"

p = ThreadPool(64)
client = storage.Client()
bucket = client.get_bucket(trigger_bucket_name)
ibucket = client.get_bucket(ibucket_name)
division = [ str(i).zfill(2) for i in range(10, 100) ] 
division += [ str(i)+"." for i in range(1,10) ]

#blobs = ibucket.list_blobs(prefix=prefix, delimiter="/")

event = { "cmd":"gcs/bin/python", \
        "params":["aggregation_reduce_query.py",
        ibucket_name, None, obucket_name, okey]
        }

res = []
cnt = 0
for sub in division:
    params = copy.deepcopy(event)
    params['params'][2] = prefix + sub + "/"
    encoded_params = base64.b64encode(bytes(json.dumps(params), "utf-8"))
    argument = (bucket, encoded_params)
    res.append(p.apply_async(invoke.invoke_storage, args=(argument,)))

n_res = []
for i in res:
    n_res.append(i.get())

p.close()
p.join()
