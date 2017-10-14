import os
import glob
import json
import pickle
from pprint import pprint as pp

bin_size = [100, 200, 400, 800, 1600, 3000]

# loop:1, matrix_size: 1024
conf = ["1_1024"]

df = []

def get_numbers(x):
    try:
        if x[:5] == "curl." and x[-7:] == ".result":
            tmp = x[5:]
            return int(tmp[:-7])
    except:
        return None

def get_realtime(x):
    """

    real    0m4.791s
    user    0m0.032s
    sys 0m0.000s
    """
    if not os.path.isfile(x):
        return 0
    with open(x) as f:
        timeval = f.read().split("\n")[1].split("\t")[1]
        mins, secs = timeval.split("m")
        secs = secs[:-1]
        return int(mins) * 60.0 + float(secs)

rdi = {}
for h in ['azure']:
    rdi[h] = { 'cnt' : 0 }
    for i in bin_size:
        if i not in rdi[h]:
            rdi[h][i] = { 'cnt' : 0 }
        for j in conf:
            if j not in rdi[h][i]:
                rdi[h][i][j] = { 'cnt' : 0 }
            cur_path = "{0}/{1}/{2}".format(h,i,j)
            for k in os.listdir(cur_path):
                if k not in rdi[h][i][j]:
                    rdi[h][i][j][k] = { 'cnt' : 0 }
                f_dir = "{0}/{1}".format(cur_path, k)
                files = [ get_numbers(x) for x in os.listdir(f_dir) ]
                files = [ x for x in files if isinstance(x, int) ]
                files.sort()
                try:
                    start = files[0]
                    end = i
                except IndexError as e:
                    start = end = 0

                # Old results in type of curl.*.result
                for l in range(start, start + end):
                    # parsing curl results
                    result_filename = "{0}/curl.{1}.result".format(f_dir, l)
                    time_filename = "{0}/time.{1}.txt".format(f_dir, l)
                    elapsed = get_realtime(time_filename)
                    if os.path.isfile(result_filename):
                        with open(result_filename) as f:
                            res = f.read().strip('"').replace(" ", "").split(",")
                            if len(res) == 5:
                                # GFLOPs, vms, rss, import time, entire time
                                res = [ float(x) for x in res ]
                                df.append([h, i, j, k, l] + res + [elapsed])
                            else:
                                res = [0.0] * 5
                                df.append([h, i, j, k, l] + res + [elapsed])
                            rdi[h]['cnt'] += 1
                            rdi[h][i]['cnt'] += 1
                            rdi[h][i][j]['cnt'] += 1
                            rdi[h][i][j][k]['cnt'] += 1
                # new results in a json format
                if start == 0 and end == 0:
                    jfiles = glob.glob(f_dir + "/*.result")
                    for jfile in jfiles:
                        with open(jfile) as f:
                            rdict = json.load(f)
                            for k1, v1 in rdict.iteritems():
                                l = int(k1)
                                res = ""
                                if v1['result']:
                                    res = v1['result'].strip('"').replace(" ",
                                            "").split(",")
                                if len(res) == 5:
                                    elapsed = v1['elapsed_time']
                                    res = [ float(x) for x in res ]
                                    df.append([h, i, j, k, l] + res + [elapsed])
                                else:
                                    res = [0.0] * 5
                                    df.append([h, i, j, k, l] + res + [elapsed])
                                rdi[h]['cnt'] += 1
                                rdi[h][i]['cnt'] += 1
                                rdi[h][i][j]['cnt'] += 1
                                rdi[h][i][j][k]['cnt'] += 1


with open("results.list", "wb") as fp:
    pickle.dump(df, fp)

pp(rdi)
#pp (df, indent=2, depth=10)
