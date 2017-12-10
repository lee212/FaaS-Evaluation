import json
import sys

if len(sys.argv) < 5:
    print "file_name keyname command_to_parse template"
    print "eg. read_result.py " + \
    "invoke.REST.100.timeout-python.usecond\:1cid\:99.False.log msg " + \
    "\".split(' ')[0].split(':')[1].split(',')[2]\" \",{},google,python\""
    sys.exit()
fname = sys.argv[1]
keyname = sys.argv[2]
parsing_str = sys.argv[3]
template = sys.argv[4]

with open(fname) as f:
    data = json.load(f)
    for k,v in data.iteritems():
        msg = v[keyname]
        exec("t = msg" + parsing_str)
        t = float(t) * 1e-3
        exec("t2 = \"" + template + "\".format(t)")
        print t2
