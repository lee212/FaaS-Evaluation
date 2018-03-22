import os
import marshal
import sys
import time
from google.cloud import storage

client = storage.Client()

ibucketname = sys.argv[1]
fpath = sys.argv[2]
fname = os.path.basename(fpath)

gsd_start = time.time()
ibucket = client.get_bucket(ibucketname)
blob = ibucket.get_blob(fpath)
lines = blob.download_as_string()
gsd_end = time.time()

result = { "result": { "gs_download": gsd_end - gsd_start, "input": { "params": sys.argv} }}
print result
