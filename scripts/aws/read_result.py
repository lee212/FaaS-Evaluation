import sys
import json

fname = sys.argv[1]
key =  sys.argv[2]
template = sys.argv[3]

with open(fname) as f:
    dat = json.load(f)
    for v in dat:
        exec('val = v' + key)
        #print "{},{},{}".format(v['duration']*1e-3, v['client_info']['elapsed_time'],
        exec("print \"" + template + "\".format(val)")

