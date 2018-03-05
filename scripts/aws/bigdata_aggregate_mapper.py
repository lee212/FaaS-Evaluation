import copy
import boto3
import invoke
from multiprocessing.pool import ThreadPool

bucket = "big-data-benchmark"
prefix = "pavlo/text/5nodes/uservisits/"
func_name = "bigdata-aggregate"
obucket = "bigdata-lee212"
okey = "aggregate.reduce"
query = { "q2a":  8, "q2b": 10, "q2c": 12 }
x = query['q2a']
event = {
        "function_name": func_name,
        "bucket": bucket,
        "key": None,
        "obucket": obucket,
        "okey": okey,
        "x": x
        }
p = ThreadPool(64)

client = boto3.client("s3")

paginator = client.get_paginator("list_objects")
page_iterator = paginator.paginate(Bucket = bucket, Prefix = prefix)
all_keys = []
all_objs = []
for page in page_iterator:
    if "Contents" in page:
        keys = [x['Key'] for x in page['Contents']]
    else:
        keys = []
    all_keys += keys
    all_objs.append(page['Contents'])

s3d_elapsed = 0
all_data = {}
res = []
for key in all_keys:
    params = copy.deepcopy(event)
    params['key'] = key
    res.append(p.apply_async(invoke.lambda_invoke, args=(params,)))
   
nres = []
for i in res:
    nres.append(i.get())

p.close()
p.join()
