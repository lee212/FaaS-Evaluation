import os
import json
import time

venv_start = time.time()
import sys, os.path
sys.path.append(os.path.abspath(os.path.join("/home/", 'azure-storage-blob/Lib/site-packages')))
from azure.storage.blob import BlockBlobService
venv_end = time.time()

def main():
    #container_name="pavlo"
    #blob_name="text/5nodes/rankings/part-00000"

    s3d_start = time.time()
    postreqdata = json.loads(open(os.environ['req']).read())
    accountname=postreqdata['account_name']
    accountkey=postreqdata['account_key']
    container_name = postreqdata["bucket"]
    blob_name = postreqdata["fname"]
    x = postreqdata['x']

    block_blob_service = BlockBlobService(account_name=accountname, account_key=accountkey) 
    blob = block_blob_service.get_blob_to_bytes(container_name, blob_name)
    lines = blob.content.split(b"\n")
    res = []
    s3d_end = time.time()

    t_start = time.time()
    for line in lines:
        try:
            pageURL, pageRank, avgDuration = line.split(",")
        except:
            continue
        # SELECT pageURL, pageRank FROM rankings WHERE

        # pageRank > X
        if int(pageRank) > int(x):
            res.append([pageURL, pageRank])

    t_end = time.time()

    r_num = len(res)
    elapsed = t_end - t_start

    response = open(os.environ['res'], 'w')
    result = {"result":{"cnt": r_num, "elapsed":elapsed, "s3_elapsed": s3d_end - s3d_start, "venv_elapsed": venv_end - venv_start},
                "params": postreqdata }
    #Log
    print (result)
    response.write(json.dumps(result))
    response.close()

main()
