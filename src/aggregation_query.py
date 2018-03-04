import sys
import time
"""

UserVisits
Stores server logs for each web page

sourceIP VARCHAR(116)
destURL VARCHAR(100)
visitDate DATE
adRevenue FLOAT
userAgent VARCHAR(256)
countryCode CHAR(3)
languageCode CHAR(6)
searchWord VARCHAR(32)
duration INT

"""

fname = sys.argv[1]
x = sys.argv[2]

f = open(fname)
lines = f.readlines()
res = {}
t_start = time.time()
for line in lines:
    sourceIP, destURL, visitDate, adRevenue, rest = line.split(",",4)
    # SELECT SUBSTR(sourceIP, 1, X), SUM(adRevenue) FROM uservisits GROUP BY
    # SUBSTR(sourceIP, 1, X)
    key = sourceIP[:int(x)]
    if key in res:
        res[key] += float(adRevenue)
    else:
        res[key] = float(adRevenue)

t_end = time.time()

r_num = len(res)
elapsed = t_end - t_start
import json
n = json.dumps(res)
with open(fname + ".aggregate", "w") as f:
     json.dump(res, f, indent=4)
print (elapsed, r_num, sys.getsizeof(n))
