# example of use

# python get_fwrite.py
# invoke.REST.100.fwrite-python.ufsize\:102400cid\:99.False.log msg 2 ,
# "gfunctions,python" >> gfunctions.fwrite.data

import json
import sys

fname = sys.argv[1]
key = sys.argv[2]
loc = int(sys.argv[3])
if len(sys.argv) > 4:
    delimeter = sys.argv[4]
else:
    delimeter = ","
template = sys.argv[5]

with open(fname) as f:
    data = json.load(f)
    for k, v in data.iteritems():
        #if key in v:
            #value = v[key].split(delimeter)[loc]
            #value = v[key].split()[0].split(":")[1].split(",")[0:3]
            #value[0] = str(int(value[0])*1024)
            #nval = ",".join(value)
            nval = eval("v{}".format(key))
            #value = nval.split(",")
            #value[0] = str(int(value[0])*1024)
            #nval = ",".join(value)

            print "{},{}".format(nval, template)


