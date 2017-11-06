import sys
import json
import requests
import os

fname = sys.argv[1]
url = 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/_/activations/'
auth_string = os.environ['IBM_OPENWHISK_AUTH_STRING']

with open(fname) as f:
    r = json.load(f)

actlist = r.keys()

tdlist = []
actdict = {}
for i in actlist:
    tdiff = 0
    # curl -H 'Authorization: Basic
    # NTNjNmY5ZDctM2JhYy00YjQ1LWI3N2ItNGVhMDMzYzg5YmUwOmNjTWxnaW5GU1VtZENuNGI0aWwxb0RaMVI2RlRNdm9QNUdtaUdlc3A3d25ucDR4QjdKQjZzUVpFQzBkTlZjclI='
    # -L
    # 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/_/activations/2cd2e85819ba4a9592e85819ba5a957e'
    headers = {'Authorization': auth_string}
    rdata = requests.get(url + i, headers=headers)
    rdict = rdata.json()
    mseconds = float(rdict['duration']) / 1000.0
    # 4443,1,1024,5.86704090704,0.366025
    cid, loop, mat_n, gflops, elapsed = rdict['response']['result']['msg'].split(",")
    tdiff = mseconds - float(elapsed)
    tdlist.append(tdiff)
    actdict[i] = rdict

with open(fname + ".tdlist", "w") as f:
    json.dump(tdlist, f)

with open(fname + ".activation", "w") as f:
    json.dump(actdict, f)


