import botocore.session
import json
import multiprocessing as mp
import sys

s = botocore.session.get_session()
c = s.create_client('lambda', region_name='us-east-2')
def invoke(x):
    func_name, num, mat_n = x
    r = c.invoke(FunctionName=func_name,
        Payload=json.dumps({'number_of_loop':int(num),
            'number_of_matrix':int(mat_n)}),
        InvocationType='Event')
    return r

def handler(event):
    p = mp.Pool(64)
    res = []
    size = int(event['invoke_size'])
    func_name = event['function_name']
    num = event['number_of_loop']
    mat_n = event['number_of_matrix']
    argument = (func_name, num, mat_n)
    for i in range(size):
        res.append(p.apply_async(invoke, args=(argument,)))

    nres = []
    for i in res:
        nres.append(i.get())

    return nres
   
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print "invoke_size func_name num mat_n"
        sys.exit()
    isize = sys.argv[1]
    func_name = sys.argv[2]
    num = sys.argv[3]
    mat_n = sys.argv[4]

    func_names = func_name.split(",")
    res = []
    for func_name in func_names:
        event = { "function_name": func_name,
                "invoke_size": isize,
                "number_of_loop": num,
                "number_of_matrix": mat_n }
        res.append(handler(event))

    print res
