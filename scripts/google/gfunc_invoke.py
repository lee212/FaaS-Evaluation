import multiprocessing as mp
from subprocess import check_output
from datetime import datetime as dt
import json
import sys

def parse_response(text):
    ''' sample res
    executionId: rb14hi9ulgqe
    result: "msg:undefined,1,1024,3.88966467865,47328 stdout:curl: tar: rm: curl:
    bash:\
              \ 3889664678.65\n stderr:curl: tar: rm: curl: bash: "
    '''
    res = text.split("\n", 1)
    # executionId
    k0, v0 = res[0].split(": ")
    k1, v1 = res[1].split(": ", 1)
    msg = v1.strip().split(" ",1)[0].split(":")[1]
    return {"key": v0,
            "msg": msg,
            "raw": text}
def invoke(args):
    cmd, params = args
    res = check_output(cmd.split() + [json.dumps(params)])
    return res

def invoker(size, fname, loop, mat_n):
    p = mp.Pool(64)
    res = []
    for i in range(int(size)):
        params = {"cid": i, "number_of_loop":int(loop), "number_of_matrix": int(mat_n)}
        cmd = "gcloud beta functions call {} --data".format(fname)
        argument = (cmd, params)
        res.append(p.apply_async(invoke, args=(argument,)))

    rall = {}
    for i in res:
        r = i.get()
        rdict = parse_response(r)
        rall[rdict['key']] = rdict
    with open("invoke.{}.{}.{}.{}.log".format(size, fname, loop, mat_n), "w") as f:
            json.dump(rall, f)

if __name__ == "__main__":

    if len(sys.argv) < 5:
        print "invoke_size func_name num mat_n"
        sys.exit()
    size = sys.argv[1]
    fname = sys.argv[2]
    loop = sys.argv[3]
    mat_n = sys.argv[4]
    invoker(size, fname, loop, mat_n)
