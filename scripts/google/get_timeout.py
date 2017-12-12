import json
import sys

res_fname = sys.argv[1]
log_fname = sys.argv[2]
template = sys.argv[3]

log_dict = {}
with open(log_fname) as f:
    data = json.load(f)
    for v in data:
        for v2 in v:
            if v2['log'].find("Function execution took") < 0:
                continue
            duration = v2['log'].split()[3]
            eid = v2['execution_id']
            log_dict[eid] = duration

with open(res_fname) as f:
    data = json.load(f)
    for k, v in data.iteritems():
        elapsed_by_client = v['client_info']['elapsed_time']
        duration = log_dict[k]
        print "{},{},{}".format(float(duration) * 1e-3, elapsed_by_client,
                template)

