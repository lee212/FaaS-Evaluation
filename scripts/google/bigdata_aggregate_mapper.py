"""
python invoke.py 1 pythonGCS
'{"cmd":"gcs/bin/python","params":["aggregation_map_query.py",
"bigdata-pavlo","text/5nodes/uservisits/part-00000",12, "bigdata-lee212"]}'
--call_type STORAGE --option bigdata-aggregate-mapper-trigger-lee212
"""
import copy
import json
import invoke
import base64
from google.cloud import storage
from multiprocessing.pool import ThreadPool

trigger_bucket_name = "bigdata-aggregate-mapper-trigger-lee212"
prefix = "text/5nodes/uservisits/"
x = 12
ibucket_name = "bigdata-pavlo"
obucket_name = "bigdata-lee212"
p = ThreadPool(64)
client = storage.Client()
bucket = client.get_bucket(trigger_bucket_name)
ibucket = client.get_bucket(ibucket_name)
blobs = ibucket.list_blobs(prefix=prefix)

event = { "cmd":"gcs/bin/python", \
        "params":["aggregation_map_query.py",
        ibucket_name, None, x, obucket_name]
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
