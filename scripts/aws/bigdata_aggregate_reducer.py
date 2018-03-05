import os
import math
import boto3
import time
import invoke
import copy
import argparse
from multiprocessing.pool import ThreadPool

okey = "aggregate.result/"
func_name = "bigdata-aggregate-reduce"
client = boto3.client("s3")

def get_object_keys(bucket, prefix, Delimiter=None):

    # 1000 is maximum without paginator
    paginator = client.get_paginator("list_objects")
    if Delimiter:
        page_iterator = paginator.paginate(Bucket = bucket, Prefix = prefix,
                Delimiter=Delimiter)
    else:
        page_iterator = paginator.paginate(Bucket = bucket, Prefix = prefix)
    all_keys = []
    all_objs = []
    for page in page_iterator:
        if "Contents" in page:
            keys = [x['Key'] for x in page['Contents']]
            all_objs.append(page['Contents'])
        elif "CommonPrefixes" in page:
            keys = [x['Prefix'] for x in page['CommonPrefixes']]
            all_objs.append(page)
        all_keys += keys
    return { "keys": all_keys, "obj": all_objs }

def get_object_prefixes(bucket, prefix):
    return get_object_keys(bucket, prefix, "/")

def get_argument():
    parser = argparse.ArgumentParser("reducer job manager")
    parser.add_argument("-b","--bucket", help="bucket")
    parser.add_argument("-p","--prefix", help="prefix of object path")
    args = parser.parse_args()
    return args

def invoke_lambda(params):
    params['function_name'] = func_name
    params['okey'] = okey
    keys = get_object_keys(params['bucket'], params['prefix'])['keys']
    params['keys'] = keys[:]
    return invoke.lambda_invoke(params)

def main(args):
    # Reading Mapper results
    # Assuming all mappers are done
    s_time = time.time()
    prefixes = get_object_prefixes(args.bucket, args.prefix)['keys']
    e_time = time.time()
    print ("first list_objects:{}".format(e_time - s_time))
    # remove directory name
    if args.prefix in prefixes:
        prefixes.remove(args.prefix)

    res = []
    nkeys = {}
    p = ThreadPool(64)
    for prefix in prefixes:
        params = { "bucket": args.bucket,
                "prefix" : prefix }
        res.append(p.apply_async(invoke_lambda, args=(params,)))

    nres = []
    for i in res:
        nres.append(i.get())

    p.close()
    p.join()

if __name__ == "__main__":
    args = get_argument()
    main(args)
