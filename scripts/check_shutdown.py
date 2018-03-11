import os
import json
from aws import invoke as ainvoke
from google import invoke as ginvoke
from azure import invoke as azinvoke
from ibm import invoke as iinvoke
import time
import argparse
import logging

logging.basicConfig(level=logging.INFO)
#logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

def get_argparse():
    parser = argparse.ArgumentParser("measure function expire time")
    parser.add_argument("-s", "--serverless", help = "provider" + 
    " aws|google|ibm|azure")
    parser.add_argument("-f", "--fname", help = "function to run")
    parser.add_argument("-p", "--param", help = "function parameter to process")
    parser.add_argument("-t", "--timeout", type=float, help = "time to stop function" + \
            "invocation in minute")
    parser.add_argument("-i", "--interval", type=float, help = "interval between invocation"
            + " in second")
    parser.add_argument("-c", "--concurrent", help = "concurrent invocation size")
    args = parser.parse_args()
    return args

def get_function_name(provider):
    if provider == "aws":
        return ainvoke.lambda_invoke
    elif provider == "google":
        return ginvoke.invoke_rest
    elif provider == "azure":
        return azinvoke.azure_invoke
    elif provider == "ibm":
        return iinvoke.invoke_rest

def main(args):

    param = { "function_name" : args.fname }
    # preparation
    if args.serverless == "aws":
        # For AWS
        ainvoke.itype = "RequestResponse"
    elif args.serverless == "google":
        # For Google
        d_project, d_region = ginvoke.config_parser(ginvoke.gcloud_config)
        param["project"] = d_project
        param["region"] = d_region
    elif args.serverless == "azure":
        pass
    elif args.serverless == "ibm":
        tmp = iinvoke.get_config()
        param = { **param, **tmp }
        param["sync"] = "false"

    if args.param:
        param_input = json.loads(args.param)
        param = { **param, **param_input }
    interval = args.interval
    res = []
    func = get_function_name(args.serverless)
    ctime = stime = time.time()
    while True:
        stime = time.time()
        tmp = func(param)
        res.append(tmp)
        logger.info("{},{}:{}".format(len(res), interval, tmp))
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
    utils.to_file("{}.{}.{}.result".format(os.path.basename(__file__).split(".")[0],args.fname,
        args.serverless),
            res)

