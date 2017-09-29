import json
from collections import OrderedDict
import subprocess

jdict = {}
ordered = OrderedDict()

import re

# https://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in
            re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def find_close(llist, num, offset):
    ref = 'flops'+str(num+offset)
    if ref in llist:
        return llist[ref]
    else:
        return find_close(llist, num+offset, offset)

def flatten(location):
    l = location.replace(" ", "")
    l = l.lower()
    return l

def conv(name, loc):
    n = name.replace("-","0",1)
    n = n.replace("-","",1)
    n = n.replace("-"+loc, "")
    return n

fout = open("create_again_missing_func.log", "a")

with open('flist') as f:
    jdata = json.load(f)
    for i in jdata:
        jdict[i['name']] = i
    #diff
    allkeys = [ 'flops' + str(i) for i in range(1,2900) ]
    diff = set(allkeys) - set(jdict.keys())
    ndiff = []
    for i in diff:
        if int(i[5:]) < 500:
            continue
        ndiff.append(i)
    missing = natural_sort(ndiff)
    t=0
    for i in missing:
        num = int(i[5:])
        if num != 1782 and t == 0:
            continue
        else:
            t=1
        if num % 100 == 0:
            ref = find_close(jdict, num, 1)
        else:
            ref = find_close(jdict, num, -1)
        rgroup = ref['resourceGroup']
        location = flatten(ref['location'])
        storage = conv(rgroup, location)
        cmd=("az functionapp create -g {0} -n {1} -s {2}" \
        + " --consumption-plan-location {3}" \
        + " --debug --verbose").format(rgroup, i, storage, location)
        print cmd
        result = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
        fout.write(result)

    fout.close()
