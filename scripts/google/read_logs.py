import json
import sys
import subprocess

fname = sys.argv[1]
keyname = sys.argv[2]
exec_expr = sys.argv[3]

with open(fname) as f:
    r = json.load(f)

tdlist = []
loglist = []
for k, v in r.iteritems():
    tdiff = 0.0
    # msg:611,1,1024,4.77169744852,790 stdout:bash: 4771697448.52\n stderr:bash: 
    # msg:53,10,1024,2.006760956,11488,false 
    try:
        if exec_expr:
            MESSAGE=v[keyname]
            exec(exec_expr)
        else:
            cid, loop, mat_n, gflops, elapsed, init_numpy = v['msg'].split(" ", 1)[0].split(":")[1].split(",")
    except Exception as e:
        print sys.exc_info()
        print v
        continue
    elapsed = float(elapsed)
    # TODO: Replace gcloud with api
    # Python api: google-cloud-logging
    # or SDK: from googlecloudsdk.api_lib.logging import common
    cmd = ('gcloud beta functions logs read --execution-id {} --format json'.format(k))
    res = subprocess.check_output(cmd.split())
    rdict = json.loads(res)
    loglist.append(rdict)

    # Assume third [2] records contains:
    # e.g. 'Function execution took 849 ms, finished with status code: 200'
    try:
        mseconds = float(rdict[1]['log'].split()[3])
    except Exception as e:
        print sys.exc_info(), e
        # [{u'time_utc': u'2017-12-10 21:19:42.181', u'name': u'timeout-nodejs',
        # u'log': u'Function execution started', u'execution_id':
        # u'u3aato7hduvp', u'level': u'D'}, {u'time_utc': u'2017-12-10
        # 21:19:43.192', u'name': u'timeout-nodejs', u'log': u'Function
        # execution took 1012 ms, finished with status code: 200',
        # u'execution_id': u'u3aato7hduvp', u'level': u'D'}]
        print rdict
        continue

    tdiff = mseconds - elapsed
    tdlist.append(tdiff)

with open(fname + ".tdlist", "w") as f:
    json.dump(tdlist, f)

with open(fname + ".stackdriver", "w") as f:
    json.dump(loglist, f)
