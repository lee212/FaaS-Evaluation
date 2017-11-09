import json
import sys
import math

per_request = 0.0000004 

base_price = { 128: 0.000000231,
        256: 0.000000463,
        512: 0.000000925,
        1024: 0.000001650,
        2048: 0.000002900 }

if len(sys.argv) < 2:
    print "stackdriver_log_file memory_size"
    sys.exit()

fname = sys.argv[1]
mem_size = int(sys.argv[2])

with open(fname) as f:
    r = json.load(f)

msec = 0
for i in r:
    try:
        msec += int(i[2]['log'].split()[3])
    except:
        print i
        continue

total_request = per_request * len(r)
total_seconds = math.ceil(msec / 1000.0)
total_price = total_request +  (base_price[mem_size] * total_seconds)
print "{} invoked for {} seconds, total price: {}".format(len(r), total_seconds, total_price)
