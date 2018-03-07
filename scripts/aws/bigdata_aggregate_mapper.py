import time
import copy
import boto3
import invoke
import argparse
from bigdata import aggregate_mapper
from multiprocessing.pool import ThreadPool
import logs

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

def local_handler(event):
    return aggregate_mapper.lambda_handler(event, None)

def main(local=False):
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
    if local:
        func = local_handler
        event["okey"] += ".local"
    else:
        func = invoke.lambda_invoke

    for key in all_keys:
        params = copy.deepcopy(event)
        params['key'] = key
        res.append(p.apply_async(func, args=(params,)))
       
    nres = []
    for i in res:
        nres.append(i.get())

    p.close()
    p.join()
    return nres

def get_argparse():
    parser = argparse.ArgumentParser("Bigdata Aggregation query - mapper")
    parser.add_argument("--local", default=False, action="store_true", help="local execution, no lambda invocation")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_argparse()
    start = time.time()
    res = main(args.local)
    end = time.time()
    logs.to_file("bigdata-mapper.result", res)
    logs.to_file("bigdata-mapper.time", {"mapper_handler": end - start })

