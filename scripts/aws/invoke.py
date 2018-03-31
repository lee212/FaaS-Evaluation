import copy
import uuid
import argparse
import os
import sys
import time
import json
import botocore.session
from multiprocessing.pool import ThreadPool
import logging
from datetime import datetime

region = "us-east-2"
itype = "RequestResponse" #"Event"
itype = "Event"
s = botocore.session.get_session()
c = s.create_client('lambda', region_name=region)

logging.basicConfig(level=logging.INFO)
#logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

def lambda_invoke(x):
    start = time.time()
    x['timestamp_from_client'] = start
    x['date_from_client'] = \
            datetime.utcfromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    res = c.invoke(FunctionName=x['function_name'], Payload=json.dumps(x),
            InvocationType=itype) 
    end = time.time()
    try:
        ret = res['Payload'].read()
    except:
        ret = None

    # elapsed_time is valid when RequestResponse used
    res['client_info'] = { 'elapsed_time' : end - start,
            'ingestionTime': end,
            'timestamp': start,
            'invocation_type': itype,
            'return_value': str(ret),
            'payload': x }
    return res

def handler(event, args):
    parallel = args.concurrent
    if not parallel:
        global itype
        # run a function in
        itype = "RequestResponse"

    # meaningless call for initialization
    func_name = event['function_name'].split(":")[0]
    c.publish_version(FunctionName=func_name)

    p = ThreadPool(64)
    res = []
    stime = time.time()
    for i in range(event['invoke_size']):
        params = copy.deepcopy(event)
        params['cid'] = i # uuid.uuid1())
        if parallel:
            res.append(p.apply_async(lambda_invoke, args=(params,)))
        else:
            res.append(lambda_invoke(params))

    mtime = time.time()
    nres = []
    if parallel:
        for i in res:
            nres.append(i.get())
    else:
        nres = res

    p.close()
    p.join()

    etime = time.time()
    # Not saving 'Payload': <botocore.response.StreamingBody object at
    # 0x7f6a9ab62510>,
    for j in nres:
        del (j['Payload'])

    tmp = {'client_info': {'start_time': "{}".format(stime),
            "end_time": "{}".format(etime),
            "threadpool": "{}".format(mtime-stime),
            "Response": "{}".format(etime-mtime),
            "total": "{}".format(etime-stime)}
            }
    nres.append(tmp)

    return nres

def argument_parser(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(description="AWS Lambda invocation")
    parser.add_argument('isize', metavar='cnt', type=int, help='number of'
            + ' invocation')
    parser.add_argument('func_names', metavar='fnames', type=str, help='Function'
            + ' name(s) to invoke')
    parser.add_argument('params', metavar='params', type=str, help='parameters'
            + ' to a function (json)')
    parser.add_argument('--concurrent', action='store_true', dest='concurrent', 
            default=False, help='Concurrency concurrent|sequential')
    args = parser.parse_args()
    args.params = json.loads(args.params)
    return (args, parser)

def to_file(fname, data):    
    with open(fname, "w") as f: 
        try:
            json.dump(data, f, indent=4)
        # TypeError: <botocore.response.StreamingBody object at 0x7f38b8fecc18>
        # is not JSON serializable
        except TypeError:
            for d in data:
                del(d['Payload'])
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    (args, parser) = argument_parser()

    func_names = args.func_names.split(",")
    res = []
    for func_name in func_names:
        event = args.params
        event["function_name"] = func_name
        event["invoke_size"] = args.isize
        res += handler(event, args)

    #print res
    params_str = ''.join(e for e in str(args.params) if e.isalnum() or e == ":")
    ofname = ("{}.{}.{}.log".format(os.path.basename(__file__).split(".")[0],
        args.isize, args.func_names, params_str, args.concurrent))
    to_file(ofname, res)

