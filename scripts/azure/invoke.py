import time
import json
import sys
import os
import requests
import argparse
from pprint import pprint as pp
from urllib.parse import urlparse
from multiprocessing.pool import ThreadPool, TimeoutError
import logging
import copy

logging.basicConfig(level=logging.INFO)
#logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

call_type = "HTTP"
thread_num = 64
timeout_sec = 60 # REST TIMEOUT

def azure_invoke(payload):
    url = payload['function_name']
    #url = "https://flops{0}.azurewebsites.net/api/HttpTriggerPythonGFlops".format(n)
    #payload = {"number_of_loop": loop, "number_of_matrix": matrix}
    s = time.time()
    try:
        r = requests.post(url,data=json.dumps(payload), timeout=timeout_sec,
                headers = {'content-type': 'application/json'})
        ret = r.text
    except requests.exceptions.ReadTimeout as e:
        ret = unicode(e, 'utf-8')
    e = time.time() - s
    return (ret, e)

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

def argument_parser(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(description="Function invocation")
    parser.add_argument("target", help="Function provider name e.g." +  \
            "azure|aws|ibm|google")
    parser.add_argument('isize', metavar='cnt', type=int, help='number of'
            + ' invocation')
    parser.add_argument('func_names', metavar='fnames', type=str, help='Function'
            + ' name(s) to invoke. Azure uses HTTP URL instead, if HTTP trigger'
            + 'selected')
    parser.add_argument('params', metavar='params', type=str, help='parameters'
            + ' to a function (json)')
    parser.add_argument('--concurrent', action='store_true', dest='concurrent', 
            default=False, help='Concurrency concurrent|sequential')
    parser.add_argument("--stdout", action="store_true",  default=False,
            help="stdout")

    try:
        # For IBM OpenWhisk
        parser.add_argument('--Org', default=os.environ['IBM_ORG'],
        help='Organization name')
        parser.add_argument('--Space', default=os.environ['IBM_SPACE'], help='Space'
                + 'name')
    except KeyError:
        pass

    args = parser.parse_args()
    args.params = json.loads(args.params)
    return (args, parser)

def convert_urls_2_str(url):
    parse_result = urlparse(url)
    url_str = parse_result.hostname.split(".")[0]
    func_name = parse_result.path.split("/")[2]
    return func_name

def handler(event, args): #parallel):
    parallel = args.concurrent

    tp = ThreadPool(thread_num)
    
    cblist = [] 
    size = int(event['invoke_size'])
    params = event
    worker = globals()[args.target + "_invoke"]
    s = time.time()
    logger.debug("started threadpool")
    for cid in range(size):

        if parallel:
            params = copy.deepcopy(event)
            params['cid'] = cid
            cblist.append(tp.apply_async(worker, (params,)))
        else:
            params['cid'] = cid
            cblist.append(worker(params))

    m = time.time()
    logger.debug("ended threadpool:{}".format(m-s))
    cnt = 0
    res = {}
    for i in cblist:
        if parallel:
            try:
                n = i.get(timeout_sec)
            except TimeoutError:
                n = (cnt, None, None)
            except:
                n = (cnt, None, None)
        else:
            n = i

        res[cnt] = {
                'result': n[0],
                'elapsed_time': n[1]}
        cnt += 1

    tp.close()
    tp.join()

    e = time.time()
    logger.debug("ended get(): {}".format(e-m))
    logger.debug("elapsed total: {}".format(e-s))
    res['client_info']  = { "threadpool": "{}".format(m - s),
            "start_time": s,
            "HTTP_Response": "{}".format(e-m),
            "end_time": e,
            "total": "{}".format(e-s)}
    return res

if __name__ == "__main__":

    args, parser = argument_parser()
    event = args.params
    event['function_name'] = args.func_names
    event['invoke_size'] = args.isize
    event['target'] = args.target
    res = handler(event, args)

    params_fstr = ''.join(e for e in str(args.params) if e.isalnum() or e == ":")
    # Temporarily disabled
    params_fstr = ""

    if event['target'] == 'azure':
        func_names = convert_urls_2_str(args.func_names)
    output_fname = ("invoke.{}.{}.{}.{}.{}.log".format(call_type, args.isize,
        func_names, params_fstr, args.concurrent))
    to_file(output_fname, res)
    if args.stdout:
        pp(res, indent=4)
