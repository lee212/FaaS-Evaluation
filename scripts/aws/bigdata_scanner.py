import copy
import argparse
import invoke
from logs import to_file
from bigdata import scanner
from multiprocessing.pool import ThreadPool
from bigdata_aggregate_reducer import get_object_keys

bucket = "big-data-benchmark"
prefix = "pavlo/text/5nodes/rankings/"
func_name = "bigdata-scan"

def local_handler(event):
    return scanner.lambda_handler(event, None)

def main(x, local=False):

    keys = get_object_keys(bucket, prefix)["keys"]

    p = ThreadPool(64)
    event = { "function_name": func_name,
            "bucket": "big-data-benchmark",
            "key": None,
            "x": x
            }
    context = None
    res = []
    if local:
        func = local_handler
    else:
        func = invoke.lambda_invoke

    for key in keys:
        params = copy.deepcopy(event)
        params["key"] = key
        res.append(p.apply_async(func, args=(params,)))

    n_res = []
    for i in res:
        n_res.append(i.get())

    # Not saving 'Payload': <botocore.response.StreamingBody object at
    # 0x7f6a9ab62510>,
    for j in n_res:
        del (j['Payload'])

    p.close()
    p.join()
    return n_res

def get_argparse():
    parser = argparse.ArgumentParser("run bigdata scan query")
    parser.add_argument("-x", type=int, default=1000, help="query input for ranking > x")
    parser.add_argument("-l", "--local", default=False, action="store_true", help="run locally")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_argparse()
    """
    q1a, q1b, q1c = 1000, 1000, 10
    x = q1a
    """
    res = main(args.x, args.local)
    to_file("scanner.{}.result".format(args.x), res)
