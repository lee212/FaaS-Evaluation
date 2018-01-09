import invoke
import json
import os
import time
import sys
import time
import rand_gen
import argparse

interval = 0.2
cold_start_delay = 0

parser = argparse.ArgumentParser(description="elasticity: function invocation with rand numbers")
parser.add_argument("interval", metavar="intvl", type=float, help="time gap" + \
        " between invocation")
parser.add_argument("rand_file", type=str, help="rand numbers from a text file")
(args, parser) = invoke.argument_parser(parser)

print ("concurrency: {}".format(args.concurrent))

rand_numbers = rand_gen.rand_read(args.rand_file)

res = []

for isize in rand_numbers:

    event = args.params
    event["function_name"] = args.func_names
    # <class 'numpy.int64'>
    event["invoke_size"] =  int(isize)

    ret = (invoke.handler(event, args.concurrent))
    print ("{} invoked and sleep {}".format(isize, args.interval))
    time.sleep(args.interval)
    
    res.append({ 'result': ret,
        'invoke_size': isize})
   
with open(os.path.basename(__file__).split(".")[0] + "." + args.func_names + ".log", "w") as f:
    json.dump(res, f, indent=4)
