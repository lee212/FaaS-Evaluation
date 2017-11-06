import json
import sys
import subprocess

fname = sys.argv[1]

with open(fname) as f:
    r = json.load(f)

tdlist = []
loglist = []
for k, v in r.iteritems():
    tdiff = 0.0
    # msg:611,1,1024,4.77169744852,790 stdout:bash: 4771697448.52\n stderr:bash: 
    try:
        cid, loop, mat_n, gflops, elapsed = v['msg'].split(" ", 1)[0].split(":")[1].split(",")
    except:
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
        mseconds = float(rdict[2]['log'].split()[3])
    except:
        print rdict
        continue

    tdiff = mseconds - elapsed
    tdlist.append(tdiff)

with open(fname + ".tdlist", "w") as f:
    json.dump(tdlist, f)

with open(fname + ".stackdriver", "w") as f:
    json.dump(loglist, f)
