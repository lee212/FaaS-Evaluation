import copy
import argparse
from logs import to_file
from bigdata import scanner
from multiprocessing.pool import ThreadPool
from bigdata_aggregate_reducer import get_object_keys

bucket = "big-data-benchmark"
prefix = "pavlo/text/5nodes/rankings/"

def local_handler(event):
    return scanner.lambda_handler(event, None)

def main(x):

    keys = get_object_keys(bucket, prefix)["keys"]

    p = ThreadPool(64)
    event = { "bucket": "big-data-benchmark",
         "key": None,
         "x": x
        }
    context = None
    res = []
    for key in keys:
        params = copy.deepcopy(event)
        params["key"] = key
        res.append(p.apply_async(local_handler, args=(params,)))

    n_res = []
    for i in res:
        n_res.append(i.get())
    p.close()
    p.join()
    return n_res

def get_argparse():
    parser = argparse.ArgumentParser("run bigdata scan query")
    parser.add_argument("-x", help="query input for ranking > x")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_argparse()
    """
    q1a, q1b, q1c = 1000, 1000, 10
    x = q1a
    """
    res = main(args.x)
    to_file("scanner.{}.result".format(args.x), res)
