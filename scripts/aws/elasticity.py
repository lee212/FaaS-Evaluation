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

res = {}
idx = 0

parser = argparse.ArgumentParser(description="elasticity: function invocation with rand numbers")
parser.add_argument("interval", metavar="intvl", type=float, help="time gap" + \
        " between invocation")
parser.add_argument("rand_file", type=str, help="rand numbers from a text file")
(args, parser) = invoke.argument_parser(parser)

print ("concurrency: {}".format(args.concurrent))

rand_numbers = rand_gen.rand_read(args.rand_file)
for isize in rand_numbers:

    args.params["function_name"] = args.func_names
    args.params["invoke_size"] =  isize
    event = args.params

    if args.concurrent:
        ret = (invoke.handler(event, args.concurrent))
        print ("{} invoked and sleep {}".format(isize, args.interval))
        time.sleep(args.interval)
    else:
        ret = []
        for k in range(isize):
            event['invoke_size'] = k
            ret.append(invoke.invoke(event))
            time.sleep(args.interval)
    # Not saving 'Payload': <botocore.response.StreamingBody object at
    # 0x7f6a9ab62510>,
    for j in ret:
        # Exception: TypeError: b'""' is not JSON serializable
        j['client_info']['return_value'] = str(j['client_info']['return_value'])
        #del (j['Payload'])

    #if idx == 0:
    #    print ("cold start delay in {} seconds".format(cold_start_delay))
    #    time.sleep(cold_start_delay)
    key_name = "{}_{}".format(idx, isize)
    res[key_name] = ret
    idx += 1
   
with open(os.path.basename(__file__).split(".")[0] + "." + args.func_names + ".log", "w") as f:
    json.dump(res, f, indent=4)
