import os
import sys
import json
import time
import base64
import requests
import argparse
import configparser
from google.cloud import pubsub_v1
from google.cloud import storage
from multiprocessing.pool import ThreadPool
from subprocess import check_output
from datetime import datetime as dt

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["HOME"] + \
#        "/.config/gcloud/application_default_credentials.json"

call_type = "REST"
gcloud_config = (os.environ['HOME'] +
        '/.config/gcloud/configurations/config_default')

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

    url = ('https://{}-{}.cloudfunctions.net/{}'.format(args['region'],
        args['project'], args['function_name']))

    res = requests.post(url,
            data=json.dumps(args),
            headers={"Content-Type":"application/json"})
    e = time.time() - s
    return (res.text, e)

def invoke_pubsub(args):

    project, topic_name, size, params = args
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)
                        
    data = u'{}'.format(params)
    # Data must be a bytestring
    data = data.encode('utf-8')
    for i in range(int(size)):
        publisher.publish(topic_path, data=data)

def invoke_storage(args):
    """ call upload_from_filename Google Cloud Storage API
    Args:
       obj is a set of bucket object and filename
       where filename should exist in a local path and not an absolute path
    Return:
       n/a
    """

    bucket, fname_encoded = args
    blob = bucket.blob(fname_encoded)
    blob.upload_from_string("") # 0 byte of content but uses filename as a param

def handler(event, args):
    call_type = args.call_type
    pname = args.project
    fname = args.func_names
    region = args.region
    option = args.option
    size = args.isize
    params = event
    parallel = args.concurrent

    p = ThreadPool(64)
    res = []
    stime = dt.now()
    if call_type == "PUBSUB":
        argument = (pname, option, size, params)
        invoke_pubsub(argument)
    elif call_type == "STORAGE":
        #s = requests.Session()
        #a = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        #s.mount('https://', a)
        client = storage.Client()#_http=s)
        bucket = client.get_bucket(option)

    for i in range(int(size)):
        params["cid"] = i
        cmd = "gcloud beta functions call {} --data".format(fname)
        if call_type == "REST":
            argument = params
            argument['region'] = region
            argument['project'] = pname
            argument['function_name'] = fname
            invoke = invoke_rest
        elif call_type == "CLI":
            argument = (cmd, params)
            invoke = invoke_cli
        elif call_type == "PUBSUB":
            argument = (pname, option, size, params)
            invoke = invoke_pubsub
        elif call_type == "STORAGE":
            # zero byte of content but the filename is used as a parameter 
            # using base64 encode
            # eyJtYXRfbiI6MTI4LCJjaWQiOjF9Cg==.txt 
            # indicates { "mat_n": 128, "cid": 1 }
            encoded_params = base64.b64encode(bytes(json.dumps(params), "utf-8"))
            argument = (bucket, encoded_params)
            invoke = invoke_storage
        # parallel is only available by PUBSUB/storage according to Google Groups
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
        elif call_type == "STORAGE":
            # n/a
            continue

        rdict['client_info'] = { 'elapsed_time': r[1],
                'API': call_type }
        if rdict['key'] is None:
            rdict['key'] = cnt
        rall[rdict['key']] = rdict
        cnt += 1
    etime = dt.now()
    p.close()
    p.join()
    '''
    params_str = ''.join(e for e in str(params) if e.isalnum() or e == ":")
    with open("invoke.{}.{}.{}.{}.{}.log".format(call_type, size, fname,
        params_str, parallel), "w") as f:
        json.dump(rall, f, indent=4)
    '''

    print (etime - stime, itime - stime, etime - itime )
    rall['client_info'] = { 'start_time':'{}'.format(stime),
        "end_time": "{}".format(etime),
        "threadpool":"{}".format(itime - stime),
        "Response": "{}".format(etime - itime),
        "total": "{}".format(etime - stime)}
    return rall

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

def config_parser(conf_file=gcloud_config):
    """ Return default project, region from config file
    Note, this is not verified by Google API Document.
    Some user might not have a default value where this function assumes

    """
    config = configparser.ConfigParser()
    config.read(conf_file)
    project = config['core']['project']
    region = config['compute']['region']
    return (project, region)

def argument_parser(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(description="Google Function invocation")
    parser.add_argument('isize', metavar='cnt', type=int, help='number of'
            + ' invocation')
    parser.add_argument('func_names', metavar='fnames', type=str, help='Function'
            + ' name(s) to invoke')
    parser.add_argument('params', metavar='params', type=str, help='parameters'
            + ' to a function (json)')
    parser.add_argument('--concurrent', action='store_true', dest='concurrent', 
            default=False, help='Concurrency concurrent|sequential')
    # For Google Functions
    d_project, d_region = config_parser(gcloud_config)
    parser.add_argument('--region', default=d_region, help='region name')
    parser.add_argument('--project', default=d_project, help='project name')
    parser.add_argument('--call_type', default=call_type, help="trigger type," + 
            " REST|CLI|PUBSUB|STORAGE")
    parser.add_argument('--option', help="pub/sub topic name or storage bucket"
            + "name depends on call_type")
    args = parser.parse_args()
    args.params = json.loads(args.params)
    return (args, parser)

if __name__ == "__main__":

    args, parser = argument_parser()
    event = args.params
    event['function_name'] = args.func_names
    event['invoke_size'] = args.isize
    res = handler(event, args)

    params_fstr = ''.join(e for e in str(args.params) if e.isalnum() or e == ":")
    output_fname = ("invoke.{}.{}.{}.{}.{}.log".format(call_type, args.isize,
        args.func_names, params_fstr, args.concurrent))
    to_file(output_fname, res)
