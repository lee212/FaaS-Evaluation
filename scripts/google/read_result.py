import json
import sys

if len(sys.argv) < 4:
    print "file_name keyname template"
    print "eg. read_result.py " + \
    "invoke.REST.100.timeout-python.usecond\:1cid\:99.False.log " + \
    "['msg'].split(' ')[0].split(':')[1].split(',')[2]\" \",{},google,python\""
    sys.exit()
fname = sys.argv[1]
keyname = sys.argv[2]
template = sys.argv[3]

with open(fname) as f:
    data = json.load(f)
    for k,v in data.iteritems():
        exec('msg = v' + keyname)
        exec("print \"" + template + "\".format(msg)")
