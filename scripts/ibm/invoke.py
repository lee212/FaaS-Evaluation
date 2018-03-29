import copy
import argparse
import uuid
import time
import json
import sys
import os
import requests
import logging
from datetime import datetime as dt
from subprocess import check_output
from multiprocessing.pool import ThreadPool

call_type = "REST"
is_sync = "false" #"true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_response(text):
    ''' sample res
    {
    "arg": {
                "cid": 1,
                "number_of_loop": 1,
                "number_of_matrix": 1024
                
            },
           
    "msg": "1,1,1024,6.49846773588,0.33046"
    }
    '''
    res = json.loads(text)
    return {"key": res['arg']['cid'],
            "msg": res['msg'],
            "raw": str(res)}

def parse_response_rest(requests_response):
    """ sample
    {u'end': 1509601678375, u'name': u'gflopsopenwhisk', u'namespace':
    u'SICE_dev', u'publish': False, u'response': {u'status': u'success',
    u'result': {u'msg': u'0,1,1024,6.18746549111,0.34707', u'arg':
    {u'number_of_loop': 1, u'number_of_matrix': 1024, u'cid': 0}}, u'success':
    True}, u'logs': [], u'start': 1509601678222, u'activationId':
    u'798dd5ab7dde43418dd5ab7dde53410c', u'version': u'0.0.1', u'duration': 153,
    u'annotations': [{u'value': {u'logs': 10, u'timeout': 300000, u'memory':
    512}, u'key': u'limits'}, {u'value': u'SICE_dev/gflopsopenwhisk', u'key':
    u'path'}, {u'value': u'blackbox', u'key': u'kind'}], u'subject':
    u'lee212@indiana.edu'}
    """
    if isinstance(requests_response, str):
        return json.loads(requests_response)
    else:
        # <class 'requests.models.Response'>
        return requests_response.json()

def get_config():
    return { "Org": os.environ["IBM_ORG"], "Space": os.environ["IBM_SPACE"] }

def invoke_cli(args):
    s = time.time()
    cmd, params = args
    res = check_output(cmd.split() + [json.dumps(params)])
    e = time.time() - s
    return (res, e)

def invoke_rest(args):
    s = time.time()
    url = \
    ('https://openwhisk.ng.bluemix.net/api/v1/namespaces/{}_{}/actions/{}?blocking={}'.format(args['Org'],
        args['Space'], args['function_name'], args['sync']))

    res = requests.post(url,
            data=json.dumps(args),
            headers={"Content-Type":"application/json", "Authorization":
                os.environ['IBM_OPENWHISK_AUTH_STRING']})
    e = time.time() - s
    if args['sync'] == "true":
        res = res.text
    return (res, e)

def handler(event, args): # parallel, org, space):
    parallel = args.concurrent
    org = args.Org
    space = args.Space

    size = event['invoke_size']
    fname = event['function_name']
    p = ThreadPool(64)
    res = []
    stime = dt.now()
    for i in range(int(size)):
        params = copy.deepcopy(event)
        params['cid'] = i # str(uuid.uuid1())#i
        params['client'] = { "curr_time": "{}".format(dt.now()),
                "init_time": "{}".format(stime),
                "API": call_type,
                "blocking": is_sync }
        if call_type == "REST":
            invoke = invoke_rest
            params["Org"] = org
            params["Space"] = space
            params["function_name"] = fname
            params["sync"] = is_sync
            if not parallel:
                params["sync"] = "true"
            argument = params
        else:
            params_str = ""
            for k, v in params.iteritems():
                params_str += "-p {} {} ".format(k, v)
            cmd = "wsk action invoke /{}_{}/{} {}".format(org,space,fname,
                    params_str)
            argument = (cmd, params)
            invoke = invoke_cli
        if parallel:
            res.append(p.apply_async(invoke, args=(argument,)))
        else:
            res.append(invoke(argument))

    itime = dt.now()
    rall = {}
    cnt = 0
    for i in res:
        if parallel:
            r = i.get()
        else:
            r = i
        if call_type == "REST":
            rdict = parse_response_rest(r[0])
        else:
            rdict = parse_response(r[0])
        rdict['client_info'] = { 'elapsed_time': r[1],
                'API':  call_type,
                'sync': is_sync }

        try:
            rall[rdict['activationId']] = rdict
        except KeyError:
            rall[cnt] = rdict
        cnt += 1
    etime = dt.now()
    p.close()
    p.join()
    logging.info("{},{},{}".format(etime - stime, itime - stime, etime - itime))
    rall['client_info'] = {'start_time': '{}'.format(stime),
            'end_time': '{}'.format(etime),
            'threadpool': '{}'.format(itime - stime),
            'HTTP_Reponse': '{}'.format(etime - itime),
            'total': '{}'.format(etime - stime)}
    return rall

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

def argument_parser(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(description="IBM OpenWhisk invocation")
    parser.add_argument('isize', metavar='cnt', type=int, help='number of'
            + ' invocation')
    parser.add_argument('func_names', metavar='fnames', type=str, help='Function'
            + ' name(s) to invoke')
    parser.add_argument('params', metavar='params', type=str, help='parameters'
            + ' to a function (json)')
    parser.add_argument('--concurrent', action='store_true', dest='concurrent', 
            default=False, help='Concurrency concurrent|sequential')
    # For IBM OpenWhisk
    parser.add_argument('--Org', default=os.environ['IBM_ORG'],
    help='Organization name')
    parser.add_argument('--Space', default=os.environ['IBM_SPACE'], help='Space'
            + 'name')
    args = parser.parse_args()
    args.params = json.loads(args.params)
    return (args, parser)

if __name__ == "__main__":

    args, parser = argument_parser()
    event = args.params
    event['function_name'] = args.func_names
    event['invoke_size'] = args.isize
    res = handler(event, args)#.concurrent, org=args.Org, space=args.Space)

    params_fstr = ''.join(e for e in str(args.params) if e.isalnum() or e == ":")
    output_fname = ("invoke.{}.{}.{}.{}.{}.log".format(call_type, args.isize,
        args.func_names, params_fstr, args.concurrent))
    to_file(output_fname, res)

