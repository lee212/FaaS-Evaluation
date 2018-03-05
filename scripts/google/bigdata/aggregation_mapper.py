import os
import marshal
import sys
import time
from google.cloud import storage

client = storage.Client()
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

ibucketname = sys.argv[1]
fpath = sys.argv[2]
fname = os.path.basename(fpath)
x = sys.argv[3]
obucketname = sys.argv[4]

gsd_start = time.time()
ibucket = client.get_bucket(ibucketname)
blob = ibucket.get_blob(fpath)
lines = blob.download_as_string().split('\n')
gsd_end = time.time()

res = { str(i).zfill(2) : {} for i in range(10,100) }
for i in range(1,10):
    res[str(i) + "."] = {}
#temp2 = { str(i) + "." : {} for i in range(1,10) }
#res = { **temp1, **temp2 }
t_start = time.time()
cnt = 0
for line in lines:
    try:
        sourceIP, destURL, visitDate, adRevenue, rest = line.split(",",4)
    except:
        continue
    # SELECT SUBSTR(sourceIP, 1, X), SUM(adRevenue) FROM uservisits GROUP BY
    # SUBSTR(sourceIP, 1, X)
    key = sourceIP[:int(x)]
    key_id = key[:2]
    if key in res[key_id]:
        res[key_id][key] += float(adRevenue)
    else:
        res[key_id][key] = float(adRevenue)
        cnt += 1

t_end = time.time()
elapsed = t_end - t_start

obucket = client.get_bucket(obucketname)
gsu_start = time.time()
for k, v in res.items():
    okey = "aggregate.reduce/{}/{}".format(k, fname)
    oblob = obucket.blob(okey)
    oblob.upload_from_string(marshal.dumps(v))
gsu_end = time.time()

result = { "result": { "cnt": cnt, "elapsed": elapsed,  \
         "gs_upload": gsu_end - gsu_start, "gs_download": gsd_end - gsd_start }}
print (result)
