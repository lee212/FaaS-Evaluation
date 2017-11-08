import json
import sys
fname = sys.argv[1]
fname_of_log = sys.argv[2]

with open(fname) as f:
    r = json.load(f)

with open(fname_of_log) as f:
    r2 = json.load(f)

res = []
for i in range(len(r)):
    idx = str(i)
    w_size = int(r[idx]['workload_size'])
    num = 0
    for j in r[idx]['response']:
        try:
            key = j['ResponseMetadata']['RequestId']
        except:
            print "error {}, {}".format(idx, r[idx])
            continue
        call_date = j['ResponseMetadata']['HTTPHeaders']['date']

        try:
            rdata = r2[key]
        except:
            print key
            continue
        gflops = float(rdata['gflop'])
        elapsed = float(rdata['all_elapsed'])
        init = rdata['init_numpy'].strip()
        mat_n = int(rdata['mat_n'])
        loop = int(rdata['loop'])
        func_timestamp = int(rdata['timestamp'])
        ''' 
        {u'gflop': u'33.5728365894', u'cid': u'0', u'timestamp': 1510109902688,
                u'all_elapsed': u'10.929441', u'init_numpy': u'True\n',
                u'func_elapsed': u'0.951923', u'raw':
                u'[INFO]\t2017-11-08T02:58:22.685Z\ta8045555-c430-11e7-a06e-d9ae43281651\t0,10,1024,33.5728365894,0.951923,10.929441,True\n',
                u'mat_n': u'1024', u'loop': u'10'}
        '''
        tmp = [i, w_size, num, gflops, elapsed, init, mat_n, loop, call_date,
                func_timestamp ]
        res.append(tmp)
        num += 1

print "total invocations: {}".format(len(res))

with open(fname + ".result", "w") as f:
    json.dump(res, f, indent=4)
