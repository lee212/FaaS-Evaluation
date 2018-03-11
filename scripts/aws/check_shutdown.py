import os
import json
import invoke
import time
import argparse
import logging

logging.basicConfig(level=logging.INFO)
#logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

def get_argparse():
    parser = argparse.ArgumentParser("measure function expire time")
    parser.add_argument("-f", "--fname", help = "function to run")
    parser.add_argument("-p", "--param", help = "function parameter to process")
    parser.add_argument("-t", "--timeout", type=float, help = "time to stop function" + \
            "invocation in minute")
    parser.add_argument("-i", "--interval", type=float, help = "interval between invocation"
            + " in second")
    parser.add_argument("-c", "--concurrent", help = "concurrent invocation size")
    args = parser.parse_args()
    return args

def main(args):

    itype = "RequestResponse"

    param = { "function_name" : args.fname }
    if args.param:
        param_input = json.loads(args.param)
        param = { **param, **param_input }
    stime = time.time()
    interval = args.interval
    res = []
    while True:
        tmp = invoke.lambda_invoke(param)
        res.append(tmp)
        logger.info("{}:{}".format(len(res), tmp))
        time.sleep(interval)
        # will be increated every time
        interval += args.interval
        ctime = time.time()
        if ctime - stime > args.timeout * 60:
            break

    return res

if __name__ == "__main__":
    args = get_argparse()
    res = main(args)
    invoke.to_file("{}.{}.result".format(os.path.basename(__file__).split(".")[0],args.fname),
            res)

