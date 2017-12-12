import sys
import json

fname = sys.argv[1]
template = sys.argv[2]

with open(fname) as f:
    dat = json.load(f)
    for k, v in dat.iteritems():
        print "{},{},{}".format(v['duration']*1e-3, v['client_info']['elapsed_time'],
                template)
                


