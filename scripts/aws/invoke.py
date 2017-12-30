import argparse
import os
import sys
import time
import json
import botocore.session
from multiprocessing.pool import ThreadPool

region = "us-east-2"
itype = "RequestResponse" #"Event"
s = botocore.session.get_session()
c = s.create_client('lambda', region_name=region)

def invoke(x):
    start = time.time()
    res = c.invoke(FunctionName=x['function_name'], Payload=json.dumps(x),
            InvocationType=itype) 
    end = time.time()
    try:
        ret = res['Payload'].read()
    except:
        ret = None

    res['client_info'] = { 'elapsed_time' : end - start,
            'invocation_type': itype,
            'return_value': ret }
    return res

def handler(event, parallel):
    # meaningless call for initialization
    func_name = event['function_name'].split(":")[0]
    c.publish_version(FunctionName=func_name)

    p = ThreadPool(64)
    res = []
    for i in range(event['invoke_size']):
        event['cid'] = i
        if parallel:
            res.append(p.apply_async(invoke, args=(event,)))
        else:
            res.append(invoke(event))

    nres = []
    if parallel:
        for i in res:
            nres.append(i.get())
    else:
        nres = res

    p.close()
    p.join()

    # Not saving 'Payload': <botocore.response.StreamingBody object at
    # 0x7f6a9ab62510>,
    for j in nres:
        del (j['Payload'])

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

if __name__ == "__main__":
    (args, parser) = argument_parser()

    func_names = args.func_names.split(",")
    res = []
    for func_name in func_names:
        params = args.params
        params["function_name"] = func_name
        params["invoke_size"] = args.isize
        res += handler(params, args.concurrent)

    #print res
    params_str = ''.join(e for e in str(params) if e.isalnum() or e == ":")
    with open("{}.{}.{}.log".format(os.path.basename(__file__).split(".")[0],
        args.isize, args.func_names, params_str, args.concurrent), "w") as f:
        json.dump(res, f, indent=4)

