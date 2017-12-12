import json
import sys

fname = sys.argv[1]

with open(fname) as f:
    r = json.load(f)

sec = 0.0
for k, v in r.iteritems():
    sec += v['elapsed_time'] - 0.3
    #gflop, rss, vms, elapsed_import, elapsed_func = v['result'].split(", ")
    print sec

base_price = 0.000016
per_request = 0.20 / 1000000
total_price = (base_price * 1024 / 1024 * sec) + (len(r) * per_request)
print "{} invoked for {} seconds, total price:{}".format(len(r), sec, total_price)
