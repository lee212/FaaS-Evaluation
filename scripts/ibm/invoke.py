from multiprocessing.pool import ThreadPool
from subprocess import check_output
from datetime import datetime as dt
import json
import sys
import requests
import os
import time

call_type = "REST"
is_sync = "true"

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
    return requests_response.json()

def invoke_cli(args):
    s = time.time()
    cmd, params = args
    res = check_output(cmd.split() + [json.dumps(params)])
    e = time.time() - s
    return (res, e)

def invoke_rest(args):
    s = time.time()
    url, params = args
    res = requests.post(url,
            data=json.dumps(params),
            headers={"Content-Type":"application/json", "Authorization":
                os.environ['IBM_OPENWHISK_AUTH_STRING']})
    e = time.time() - s
    return (res, e)

def invoker(size, org, space, fname, params, parallel):
    p = ThreadPool(64)
    res = []
    stime = dt.now()
    for i in range(int(size)):
        params['cid'] = i
        if call_type == "REST":
            url = \
                    'https://openwhisk.ng.bluemix.net/api/v1/namespaces/{}_{}/actions/{}?blocking={}'.format(org,space,fname,is_sync)
            argument = (url, params)
        else:
            params_str = ""
            for k, v in params.iteritems():
                params_str += "-p {} {} ".format(k, v)
            cmd = "wsk action invoke /{}_{}/{} {}".format(org,space,fname,
                    params_str)
            argument = (cmd, params)

        if call_type == "REST":
            invoke = invoke_rest
        else:
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
    params_fstr = ''.join(e for e in str(params) if e.isalnum() or e == ":")
    with open("invoke.{}.{}.{}.{}.{}.log".format(call_type, size, fname,
        params_fstr, parallel), "w") as f:
            json.dump(rall, f, indent=2)

    print etime - stime, itime - stime, etime - itime 

if __name__ == "__main__":

    if len(sys.argv) < 7:
        print "invoke_size Org Space func_name params sequential|concurrent"
        sys.exit()
    size = sys.argv[1]
    org = sys.argv[2]
    space = sys.argv[3]
    fname = sys.argv[4]
    params = json.loads(sys.argv[5])
    parallel = True if sys.argv[6] == "concurrent" else False
    invoker(size, org, space, fname, params, parallel)
