import copy
import json
import invoke
import base64
from google.cloud import storage
from multiprocessing.pool import ThreadPool

trigger_bucket_name = "bigdata-scanner-trigger-lee212"
prefix = "text/5nodes/rankings/"
x = 1000 # 100, 10
ibucket_name = "bigdata-pavlo"
obucket_name = "bigdata-lee212"
p = ThreadPool(64)
client = storage.Client()
bucket = client.get_bucket(trigger_bucket_name)
ibucket = client.get_bucket(ibucket_name)
blobs = ibucket.list_blobs(prefix=prefix)

event = { "cmd":"gcs/bin/python", \
        "params":["scan_query.py",
        ibucket_name, None, x]
        }

res = []
cnt = 0
for blob in blobs:
    params = copy.deepcopy(event)
    params['params'][2] = blob.name
    encoded_params = base64.b64encode(bytes(json.dumps(params), "utf-8"))
    argument = (bucket, encoded_params)
    res.append(p.apply_async(invoke.invoke_storage, args=(argument,)))

n_res = []
for i in res:
    n_res.append(i.get())

p.close()
p.join()
