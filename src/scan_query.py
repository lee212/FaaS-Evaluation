import sys
import time

fname = sys.argv[1]
x = sys.argv[2]

f = open(fname)
lines = f.readlines()
res = []
t_start = time.time()
for line in lines:
    pageURL, pageRank, avgDuration = line.split(",")
    # SELECT pageURL, pageRank FROM rankings WHERE pageRank > X
    if int(pageRank) > int(x):
        res.append([pageURL, pageRank])

t_end = time.time()

r_num = len(res)
elapsed = t_end - t_start

