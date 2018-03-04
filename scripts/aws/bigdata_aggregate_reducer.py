import math
import boto3
import time
import invoke
import copy
import argparse
from multiprocessing.pool import ThreadPool

okey = "aggregate.reduce/"
client = boto3.client("s3")

def get_object_keys(bucket, prefix):

    obj = client.list_objects(Bucket = bucket, Prefix = prefix)
    keys = [x['Key'] for x in obj['Contents']]
    return { "keys": keys, "obj": obj['Contents'] }

def get_argument():
    parser = argparse.ArgumentParser("reducer job manager")
    parser.add_argument("-b","--bucket", help="bucket")
    parser.add_argument("-p","--prefix", help="prefix of object path")
    parser.add_argument("--batch_size", help="batch_size")
    args = parser.parse_args()
    return args

def main(args):
    bsize = max(2, int(args.batch_size))
    # Reading Mapper results
    # Assuming all mappers are done
    # TODO Receive number of mappers to confirm 
    s_time = time.time()
    keys = get_object_keys(args.bucket, args.prefix)['keys']
    e_time = time.time()
    print ("list_objects:{}".format(e_time - s_time))
    # remove directory name
    keys.remove(args.prefix)

    p = ThreadPool(64)
    res = []
    event = {
              "bucket": args.bucket,
              "keys": [],
              "okey": okey
              }
    reducer_size = math.ceil(len(keys) / bsize)
    for i in range(0, len(keys), bsize):
        params = copy.deepcopy(event)
        params['keys'] = keys[i:i+bsize]
        #res.append(r.apply_async(invoke.lambda_invoke, args=(params,)))

    nres = []
    for i in res:
        nres.append(i.get())

    p.close()
    p.join()

    processed = 0
    p_keys = []
    while processed < reducer_size:
        nkeys = get_object_keys(args.bucket, okey)['keys']
        # remove directory name
        nkeys.remove(okey)
        print(nkeys)
        for i in range(0, len(nkeys), bsize):
            params = copy.deepcopy(event)
            params['keys'] = nkeys[i:i+bsize]
            #res.append(r.apply_async(invoke.lambda_invoke, args=(params,)))
            p_keys = set(p_keys, params['keys'])
        processed = len(p_keys)
        time.sleep(0.1)

if __name__ == "__main__":
    args = get_argument()
    main(args)
