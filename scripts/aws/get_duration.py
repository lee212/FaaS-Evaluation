import json
import sys
import math

if len(sys.argv) < 3:
    print ("log_filename output_filename result_filename")
    sys.exit()

log_fname = sys.argv[1]
ofname = sys.argv[2]

res_r = []
try:
    res_fname = sys.argv[3]
    with open(res_fname) as f2:
        res_r = json.load(f2)
except:
    pass

with open(log_fname) as f:
    log_r = json.load(f)

res_r_reqid = {}
for i in res_r:
    res_r_reqid[i['ResponseMetadata']['RequestId']] = i

msec = 0
res = []
for i in log_r:
    loc = i['message'].find("Duration")
    if loc > 0:
        msec = float(i['message'][loc:].split(" ",2)[1])
        if res_r_reqid:
            reqid_loc = i['message'].find("RequestId")
            reqid = i['message'][reqid_loc:].split("\t",2)[0].split(": ")[1]
            client_sec = res_r_reqid[reqid]['client_info']['elapsed_time']
            print (reqid, msec / 1000, client_sec)
        else:
            res.append(msec * 0.001)

if res:
    with open(ofname, "w") as f:
        json.dump(res, f, indent=4)
