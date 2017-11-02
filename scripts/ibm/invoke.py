import multiprocessing as mp
from subprocess import check_output
from datetime import datetime as dt
import json
import sys
import requests
import os

call_type = "REST"
is_sync = "false"

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
    cmd, params = args
    res = check_output(cmd.split() + [json.dumps(params)])
    return res

def invoke_rest(args):
    url, params = args
    res = requests.post(url,
            data=json.dumps(params),
            headers={"Content-Type":"application/json", "Authorization":
                os.environ['IBM_OPENWHISK_AUTH_STRING']})
    return res

def invoker(size, org, space, fname, loop, mat_n):
    p = mp.Pool(64)
    res = []
    stime = dt.now()
    for i in range(int(size)):
        params = "-p cid {} -p number_of_loop {} -p number_of_matrix {}".format(i, loop, mat_n)
        cmd = "wsk action invoke /{}_{}/{} {}".format(org,space,fname, params)
        argument = (cmd, params)
        if call_type == "REST":
            params = {"cid": i, "number_of_loop":int(loop), "number_of_matrix": int(mat_n)}
            url = \
                    'https://openwhisk.ng.bluemix.net/api/v1/namespaces/{}_{}/actions/{}?blocking={}'.format(org,space,fname,is_sync)
            argument = (url, params)
        if call_type == "REST":
            invoke = invoke_rest
        else:
            invoke = invoke_cli
        res.append(p.apply_async(invoke, args=(argument,)))

    itime = dt.now()
    rall = {}
    cnt = 0
    for i in res:
        r = i.get()
        #rdict = parse_response(r)
        if call_type == "REST":
            rdict = parse_response_rest(r)
        else:
            rdict = parse_response(r)
        try:
            rall[rdict['activationId']] = rdict
        except KeyError:
            rall[cnt] = rdict
        cnt += 1
    etime = dt.now()
    with open("invoke.{}.{}.{}.{}.{}.log".format(call_type, size, fname, loop, mat_n), "w") as f:
            json.dump(rall, f)

    print etime - stime, itime - stime, etime - itime 

if __name__ == "__main__":

    if len(sys.argv) < 5:
        print "invoke_size Org Space func_name num mat_n"
        sys.exit()
    size = sys.argv[1]
    org = sys.argv[2]
    space = sys.argv[3]
    fname = sys.argv[4]
    loop = sys.argv[5]
    mat_n = sys.argv[6]
    invoker(size, org, space, fname, loop, mat_n)
