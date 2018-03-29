import invoke
import json
import os
import time
import sys
import time
import rand_gen
import argparse
import logging
from get_duration import get_duration

logging.basicConfig(level=logging.INFO)
#logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

interval = 0.2
cold_start_delay = 0

def elastic_invoke(args):
    """ 
    Invoke a function with concurrent numbers in file 
    """

    logger.info("concurrency: {}".format(args.concurrent))
    rand_numbers = rand_gen.rand_read(args.rand_file)

    res = []
    for isize in rand_numbers:

        event = args.params
        event["function_name"] = args.func_names
        # <class 'numpy.int64'>
        isize = int(isize)
        event["invoke_size"] = isize

        ret = (invoke.handler(event, args.concurrent))
        logger.info("{} invoked and sleep {}".format(isize, args.interval))
        time.sleep(args.interval)
        
        res.append({ 'result': ret, 'invoke_size': isize})
    return res

def to_file(fname, data):    
    with open(fname, "w") as f: 
        json.dump(data, f, indent=4)

def log_with_result(invoke_fname, log_fname):
    """
        Connects two output files by RequestId.
        This is necessary for event (async) invocation
    """
    with open(invoke_fname) as f:
        invoked_list = json.load(f)

    with open(log_fname) as f:
        log_data = json.load(f)

    res = []
    num = 0
    for i in invoked_list:
        i_size = int(i['invoke_size'])
        for j in i['result']:#['response']:
            try:
                key = j['ResponseMetadata']['RequestId']
            except:
                logger.error("error {}".format(j))
                continue
            call_date = j['ResponseMetadata']['HTTPHeaders']['date']

            try:
                rdata = log_data[key]
            except:
                logger.error(key)
                continue

            # 0 - START, 1- main message, 2- END, 3- REPORT
            msec = get_duration(rdata[3]['message'])
            if msec:
                tmp = [num, msec, i_size]
                res.append(tmp)
            num += 1

    logger.info("total invocations: {}".format(len(res)))
    return res

if __name__ == "__main__":
 
    parser = argparse.ArgumentParser(description="elasticity: function" + \
            " invocation with rand numbers")
    subparsers = parser.add_subparsers(help='sub-command help', dest='sub')
    
    parser_invoke = subparsers.add_parser('invoke', help='invoke with rand' + \
            ' numbers')
    # function names, params same as invoke.py
    parser_invoke.add_argument('func_names', metavar='fnames', type=str,
            help='Function' + ' name(s) to invoke')
    parser_invoke.add_argument('params', metavar='params', type=str,
            help='parameters' + ' to a function (json)')
    # rand_file, interval only for elastic
    parser_invoke.add_argument("rand_file", type=str, help="rand numbers from a"
            + " text file")
    parser_invoke.add_argument("--interval", metavar="intvl", type=float,
            default=interval, help="time gap" + " between invocation, " + 
            "default:{}".format(interval))
    parser_invoke.add_argument('--concurrent', action='store_true',
            dest='concurrent', default=False, help='Concurrency'
            + ' concurrent|sequential')

    parser_log = subparsers.add_parser('log', help='read logs with elasticity' +
            ' results')
    parser_log.add_argument('res_fname', help='result file of elastic invoke')
    parser_log.add_argument('log_fname', help='log file')
    args = parser.parse_args()

    if args.sub == "invoke":
        args.params = json.loads(args.params)
        result = elastic_invoke(args)
        output_fname = os.path.basename(__file__).split(".")[0] + "." + \
                args.func_names + ".log"
    elif args.sub == "log":
        result = log_with_result(args.res_fname, args.log_fname)
        output_fname = args.res_fname + ".result"

    to_file(output_fname, result)
