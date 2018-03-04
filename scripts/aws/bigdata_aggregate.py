import copy
import boto3
import invoke
from multiprocessing.pool import ThreadPool

bucket = "big-data-benchmark"
prefix = "pavlo/text/5nodes/uservisits/"
func_name = "bigdata-aggregate"
event = {
        "function_name": func_name,
        "bucket": bucket,
        "key": None,
        "obucket": "bigdata-lee212",
        "x": 12
        }
p = ThreadPool(64)

client = boto3.client("s3")
objects = client.list_objects(Bucket=bucket, Prefix=prefix)
# directory excluded
del(objects['Contents'][0])
keys = [ x['Key'] for x in objects['Contents']]
s3d_elapsed = 0
all_data = {}
res = []
for key in keys:
    params = copy.deepcopy(event)
    params['key'] = key
    res.append(p.apply_async(invoke.lambda_invoke, args=(params,)))
   
nres = []
for i in res:
    nres.append(i.get())

p.close()
p.join()
