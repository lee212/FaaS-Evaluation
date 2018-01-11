from multiprocessing.pool import ThreadPool
from subprocess import check_output
from datetime import datetime as dt
import json
import sys
import requests
import time
from google.cloud import pubsub_v1
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["HOME"] + \
        "/.config/gcloud/application_default_credentials.json"

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
    """ function invocation by gcloud """
    s = time.time()
    cmd, params = args
    res = check_output(cmd.split() + [json.dumps(params)])
    e = time.time() - s
    return (res, e)

def invoke_rest(args):
    """ function invocation by http REST API """
    s = time.time()
    url, params = args
    res = requests.post(url,
            data=json.dumps(params),
            headers={"Content-Type":"application/json"})
    e = time.time() - s
    return (res, e)

def invoke_pubsub(args):

    project, topic_name, size, params = args
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)
                        
    data = u'{}'.format(params)
    # Data must be a bytestring
    data = data.encode('utf-8')
    for i in range(int(size)):
        publisher.publish(topic_path, data=data)

def invoker(size, region, pname, fname, params, parallel, pubsub):
    p = ThreadPool(64)
    res = []
    stime = dt.now()
    if call_type == "PUBSUB":
        argument = (pname, pubsub, size, params)
        invoke_pubsub(argument)

    for i in range(int(size)):
        params["cid"] = i
        cmd = "gcloud beta functions call {} --data".format(fname)
        url = \
        'https://{}-{}.cloudfunctions.net/{}'.format(region, pname, fname)
        if call_type == "REST":
            argument = (url, params)
            invoke = invoke_rest
        elif call_type == "CLI":
            argument = (cmd, params)
            invoke = invoke_cli
        elif call_type == "PUBSUB":
            argument = (pname, pubsub, size, params)
            invoke = invoke_pubsub
        # parallel is only available by PUBSUB according to Google Groups
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
        elif call_type == "CLI":
            rdict = parse_response(r[0])
        elif call_type == "PUBSUB":
            # n/a 
            break

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
        json.dump(rall, f, indent=4)

    print (etime - stime, itime - stime, etime - itime )

if __name__ == "__main__":

    if len(sys.argv) < 7:
        print ("invoke_size region project_name " + 
                "func_name params sequential|concurrent" + 
                "call_type(REST|CLI|PUBSUB) [pub/sub topic name] ")
        sys.exit(-1)
    size = sys.argv[1]
    region = sys.argv[2]
    pname = sys.argv[3]
    fname = sys.argv[4]
    params = json.loads(sys.argv[5])
    parallel = True if sys.argv[6] == 'concurrent' else False
    call_type = sys.argv[7]
    pubsub = sys.argv[8]
    invoker(size, region, pname, fname, params, parallel, pubsub)
