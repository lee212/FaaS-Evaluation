import os
import marshal
import sys
import time
from google.cloud import storage

client = storage.Client()

def invoke_lambda(args):
    ibucketname, fpath, x = args
    fname = os.path.basename(fpath)
    gsd_start = time.time()
    ibucket = client.get_bucket(ibucketname)
    blob = ibucket.get_blob(fpath)
    lines = blob.download_as_string().split(b'\n')
    gsd_end = time.time()

    t_start = time.time()
    cnt = 0
    res = []
    for line in lines:
        try:
            pageURL, pageRank, avgDuration = line.split(b",")
        except:
            continue
        if int(pageRank) > int(x):
            res.append([pageURL, pageRank])

    r_num = len(res)
    t_end = time.time()
    elapsed = t_end - t_start

    result = { "result": { "cnt": r_num, "elapsed": elapsed,  \
            "gs_download": gsd_end - gsd_start, "input": { "params": sys.argv, "line_count": len(lines)} }}
    return result

def main():
    res = invoke_lambda(sys.argv[1], sys.argv[2], sys.argv[3])
    print (res)

if __name__ == "__main__":
    main()
