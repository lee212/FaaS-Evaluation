import os
import sys
import time
import json
import botocore.session
from multiprocessing.pool import ThreadPool

region = "us-east-2"
itype = "RequestResponse" #"Event"
s = botocore.session.get_session()
c = s.create_client('lambda', region_name=region)

def invoke(x):
    start = time.time()
    res = c.invoke(FunctionName=x['function_name'], Payload=json.dumps(x),
            InvocationType=itype) 
    end = time.time()
    res['client_info'] = { 'elapsed_time' : end - start,
            'invocation_type': itype }
    return res

def handler(event, parallel):
    p = ThreadPool(64)
    res = []
    for i in range(event['invoke_size']):
        event['cid'] = i
        if parallel:
            res.append(p.apply_async(invoke, args=(event,)))
        else:
            res.append(invoke(event))

    nres = []
    if parallel:
        for i in res:
            nres.append(i.get())
    else:
        nres = res

    p.close()
    p.join()

    # Not saving 'Payload': <botocore.response.StreamingBody object at
    # 0x7f6a9ab62510>,
    for j in nres:
        del (j['Payload'])

    return nres
   
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print "invoke_size func_name params sequential|concurrent"
        sys.exit()
    isize = int(sys.argv[1])
    func_name = sys.argv[2]
    params = json.loads(sys.argv[3])
    parallel = True if sys.argv[4] == "concurrent" else False

    func_names = func_name.split(",")
    res = []
    for func_name in func_names:
        params["function_name"] = func_name
        params["invoke_size"] = isize
        res += handler(params, parallel)

    #print res
    params_str = ''.join(e for e in str(params) if e.isalnum() or e == ":")
    with open("{}.{}.{}.log".format(os.path.basename(__file__).split(".")[0],
        isize, func_name, params_str, parallel), "w") as f:
        json.dump(res, f)

