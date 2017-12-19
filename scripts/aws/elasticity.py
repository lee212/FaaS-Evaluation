import invoke
import json
import os
import time
import sys
import time

interval = 0.2
cold_start_delay = 0

res = {}
idx = 0

(args, parser) = invoke.argument_parser()
parser.add_argument("interval", metavar="intvl", type=float, help="time gap"
        + " between invocation")
new_args = parser.parse_args()

print "{} is chosen".format(args.concurrent)

for isize in rand_numbers:

    args.params["function_name"] = args.func_names
    args.params["invoke_size"] =  args.isize
    event = args.params

    if args.concurrent == "concurrent":
        ret = (invoke.handler(event))
        print "{} invoked and sleep {}".format(args.isize, args.interval)
        time.sleep(args.interval)
    else:
        ret = []
        for k in range(args.isize):
            event['invoke_size'] = k
            ret.append(invoke.invoke(event))
            time.sleep(args.interval)
    # Not saving 'Payload': <botocore.response.StreamingBody object at
    # 0x7f6a9ab62510>,
    for j in ret:
        del (j['Payload'])

    if idx == 0:
        print "cold start delay in {} seconds".format(cold_start_delay)
        time.sleep(cold_start_delay)
    key_name = "{}_{}".format(idx, args.isize)
    res[key_name] = ret
    idx += 1
   
with open(os.path.basename(__file__).split(".")[0] + args.func_names + ".log", "w") as f:
    json.dump(res, f)
