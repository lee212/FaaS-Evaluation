import json
import sys
import math

fname = sys.argv[1]
mem = int(sys.argv[2])

with open(fname) as f:
    r = json.load(f)

msec = 0
for k, v in r.iteritems():
    msec += int(v['duration'])
    #print v['duration'], msec

base_price = 0.000017
total_sec = math.ceil(msec / 1000.0)
total_price = base_price * (mem/1024.0) *  total_sec

print "{} invoked for {} seconds. total price: {}".format(len(r), total_sec,total_price)

