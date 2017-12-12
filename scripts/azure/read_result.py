import json
import sys

fname = sys.argv[1]
key = sys.argv[2]
template = sys.argv[3]

with open(fname) as f:
    res = json.load(f)
    for k, v in res.iteritems():
        val = v[key]
        exec("print \"" + template + "\".format(val)")
