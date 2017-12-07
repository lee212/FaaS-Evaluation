import sys
import json
import botocore.session
from multiprocessing.pool import ThreadPool

region = "us-east-2"
itype = "RequestResponse" #"Event"
s = botocore.session.get_session()
c = s.create_client('lambda', region_name=region)

def invoke(x):
    func_name = x['function_name']
    r = c.invoke(FunctionName=func_name, Payload=json.dumps(x),
            InvocationType=itype) 
    return r

def handler(event, parallel):
    p = ThreadPool(64)
    res = []
    size = int(event['invoke_size'])
    func_name = event['function_name']
    for i in range(size):
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
    return nres
   
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print "invoke_size func_name params sequential|concurrent"
        sys.exit()
    isize = sys.argv[1]
    func_name = sys.argv[2]
    params = json.loads(sys.argv[3])
    parallel = True if sys.argv[4] == "concurrent" else False

    func_names = func_name.split(",")
    res = []
    for func_name in func_names:
        params["function_name"] = func_name
        params["invoke_size"] = isize
        res += handler(params, parallel)

    print res
