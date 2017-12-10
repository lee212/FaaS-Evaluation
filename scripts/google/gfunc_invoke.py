from multiprocessing.pool import ThreadPool
from subprocess import check_output
from datetime import datetime as dt
import json
import sys
import requests
import time

call_type = "REST"

def parse_response(text):
    ''' sample res
    executionId: rb14hi9ulgqe
    result: "msg:undefined,1,1024,3.88966467865,47328 stdout:curl: tar: rm: curl:
    bash:\
              \ 3889664678.65\n stderr:curl: tar: rm: curl: bash: "
    '''
    res = text.split("\n", 1)
    # executionId
    k0, v0 = res[0].split(": ")
    k1, v1 = res[1].split(": ", 1)
    msg = v1.strip().split(" ",1)[0].split(":")[1]
    return {"key": v0,
            "msg": msg,
            "raw": text}

def parse_response_rest(requests_response):
    r = requests_response
    try:
        key = r.headers['Function-Execution-Id']
    except:
        key = None

    msg = r.text
    return {"key": key,
            "msg": msg,
            "raw": json.dumps(dict(r.headers)) + str(r.elapsed)}

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
            headers={"Content-Type":"application/json"})
    e = time.time() - s
    return (res, e)

def invoker(size, region, pname, fname, params, parallel):
    p = ThreadPool(64)
    res = []
    stime = dt.now()
    for i in range(int(size)):
        params["cid"] = i
        cmd = "gcloud beta functions call {} --data".format(fname)
        argument = (cmd, params)
        url = \
        'https://{}-{}.cloudfunctions.net/{}'.format(region, pname, fname)
        argument = (url, params)
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
                'API': call_type }
        if rdict['key'] is None:
            rdict['key'] = cnt
        rall[rdict['key']] = rdict
        cnt += 1
    etime = dt.now()
    p.close()
    p.join()
    params_str = ''.join(e for e in str(params) if e.isalnum() or e == ":")
    with open("invoke.{}.{}.{}.{}.{}.log".format(call_type, size, fname,
        params_str, parallel), "w") as f:
        json.dump(rall, f)

    print etime - stime, itime - stime, etime - itime 

if __name__ == "__main__":

    if len(sys.argv) < 7:
        print "invoke_size region project_name " + \
                "func_name params sequential|concurrent"
        sys.exit(-1)
    size = sys.argv[1]
    region = sys.argv[2]
    pname = sys.argv[3]
    fname = sys.argv[4]
    params = json.loads(sys.argv[5])
    parallel = True if sys.argv[6] == 'concurrent' else False
    invoker(size, region, pname, fname, params, parallel)
