import json
import sys

fnames = sys.argv[1]

ar = []
for fname in fnames.split(","):
    with open(fname) as f:
        r = json.load(f)

    for i in r:
        if i['message'].find('1024') > 0:
            try:
                loop, mat_n, gflop, sec = i['message'].split("\t")[3].split(",")
            except:
                pass
            ar.append(float(gflop))


with open(fname + str(len(fnames)) + ".gflops", "w") as f:
    json.dump(ar, f)
