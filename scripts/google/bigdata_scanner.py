import argparse
import copy
import json
import invoke
import base64
from google.cloud import storage
from multiprocessing.pool import ThreadPool
from bigdata import scan_query

trigger_bucket_name = "bigdata-scanner-trigger-lee212"
prefix = "text/5nodes/rankings/"
x = 1000 # 100, 10
ibucket_name = "bigdata-pavlo"
obucket_name = "bigdata-lee212"

def main(local=False):
    p = ThreadPool(16)
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
    if local:
        func = scan_query.invoke_lambda
    else:
        func = invoke.invoke_storage

    for blob in blobs:
        if local:
            argument = (ibucket_name, blob.name, x)
        else:
            params = copy.deepcopy(event)
            params['params'][2] = blob.name
            encoded_params = base64.b64encode(bytes(json.dumps(params), "utf-8"))
            argument = (bucket, encoded_params)
        res.append(p.apply_async(func, args=(argument,)))

    n_res = []
    for i in res:
        tmp = i.get()
        n_res.append(tmp)

    p.close()
    p.join()
    return n_res

def get_argparse():
    parser = argparse.ArgumentParser("bigdata scanner")
    parser.add_argument("--local", default=False, action="store_true",
            help="local invocation, no google function")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_argparse()
    res = main(args.local)
    invoke.to_file("bigdata-scanner.result",res)
