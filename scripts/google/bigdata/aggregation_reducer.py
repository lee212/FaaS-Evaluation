import os
import marshal
import sys
import time
from google.cloud import storage

ibucketname = sys.argv[1]
prefix = sys.argv[2]
obucketname = sys.argv[3]
okey = sys.argv[4]

gsd_start = time.time()
ibucket = client.get_bucket(ibucketname)
blobs = ibucket.list_blobs(prefix=prefix)
gsd_end = time.time()

t_start = time.time()
all_data = {}
for blob in blobs:
    data = marshal.loads(blob.download_as_string())
    del blob
    for k, v in data.iteritems():
        if k in all_data:
            all_data[k] += v
        else:
            all_data[k] = v
        del data
del blobs
t_end = time.time()
elapsed = t_end - t_start

okey += "".join(prefix.split("/")[-2:])
gsu_start = time.time()
obucket = client.get_bucket(obucketname)
oblob = obucket.blob(okey)
oblob.upload_from_string(marshal.dumps(all_data))
gsu_end = time.time()

result = { "result": { "cnt": len(all_data), "elapsed": elapsed,  \
         "gs_upload": gsu_end - gsu_start, "gs_download": gsd_end - gsd_start }}
print result
