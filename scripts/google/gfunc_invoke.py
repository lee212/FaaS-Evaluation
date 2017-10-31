import multiprocessing as mp
from subprocess import check_output
from datetime import datetime as dt
import json
import sys
import requests

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
    cmd, params = args
    res = check_output(cmd.split() + [json.dumps(params)])
    return res

def invoke_rest(args):
    url, params = args
    res = requests.post(url,
            data=json.dumps(params),
            headers={"Content-Type":"application/json"})
    return res

def invoker(size, fname, loop, mat_n):
    p = mp.Pool(64)
    res = []
    stime = dt.now()
    for i in range(int(size)):
        params = {"cid": i, "number_of_loop":int(loop), "number_of_matrix": int(mat_n)}
        cmd = "gcloud beta functions call {} --data".format(fname)
        argument = (cmd, params)
        url = \
        'https://us-central1-capable-shard-436.cloudfunctions.net/{}'.format(fname)
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
        if rdict['key'] is None:
            rdict['key'] = cnt
        rall[rdict['key']] = rdict
        cnt += 1
    etime = dt.now()
    with open("invoke.{}.{}.{}.{}.{}.log".format(call_type, size, fname, loop, mat_n), "w") as f:
            json.dump(rall, f)

    print etime - stime, itime - stime, etime - itime 

if __name__ == "__main__":

    if len(sys.argv) < 5:
        print "invoke_size func_name num mat_n"
        sys.exit()
    size = sys.argv[1]
    fname = sys.argv[2]
    loop = sys.argv[3]
    mat_n = sys.argv[4]
    invoker(size, fname, loop, mat_n)
