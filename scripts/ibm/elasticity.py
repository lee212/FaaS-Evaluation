import invoke
import json
import os
import time
import sys
import time
import rand_gen
import argparse
import logging

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
        event["invoke_size"] =  int(isize)

        ret = (invoke.handler(event, args.concurrent))
        logger.info("{} invoked and sleep {}".format(isize, args.interval))
        time.sleep(args.interval)
        
        res.append({ 'result': ret, 'invoke_size': int(isize)})
    return res

def to_file(fname, data):    
    with open(fname, "w") as f: 
        json.dump(data, f, indent=4)

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

    args = parser.parse_args()

    if args.sub == "invoke":
        args.params = json.loads(args.params)
        org, space = invoke.get_config()
        args["Org"] = org
        args["Space"] = space
        result = elastic_invoke(args)
        output_fname = os.path.basename(__file__).split(".")[0] + "." + \
                args.func_names + ".log"

    if 'output_fname' in locals():
        to_file(output_fname, result)
