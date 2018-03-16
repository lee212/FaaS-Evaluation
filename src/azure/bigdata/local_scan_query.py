import os
import json
import time
import sys, os.path
import argparse
from multiprocessing.pool import ThreadPool
from azure.storage.blob import BlockBlobService

def scan_file(postreqdata):
    """
        Test run:
        curl -X POST -d "{\"account_name\":None, \"account_key\": None, 
                        \"bucket\": \"pavlo\",\"fname\":
                        \"text/5nodes/rankings/part-00000\",
                        \"x\": 1000}"
                        'https://test.azurewebsites.net/api/HttpTriggerPython31'
        Sample Params:
        {
            "account_name": xxx,
            "account_key": xxx,
            "bucket": "pavlo",
            "fname": "text/5nodes/rankings/part-00000",
            "x": 1000
        }
    """
    #container_name="pavlo"
    #blob_name="text/5nodes/rankings/part-00000"

    s3d_start = time.time()
    #postreqdata = json.loads(open(os.environ['req']).read())
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
            pageURL, pageRank, avgDuration = line.split(b",")
        except:
            continue
        # SELECT pageURL, pageRank FROM rankings WHERE

        # pageRank > X
        if int(pageRank) > int(x):
            res.append([pageURL, pageRank])

    t_end = time.time()

    r_num = len(res)
    elapsed = t_end - t_start

    #response = open(os.environ['res'], 'w')
    result = {"result":{"cnt": r_num, "elapsed":elapsed, "s3_elapsed": s3d_end - s3d_start, },
                "params": postreqdata }
    return result
    #Log
    #print (result)
    #response.write(json.dumps(result))
    #response.close()

parser = argparse.ArgumentParser("local azure function call")
parser.add_argument("--account_name")
parser.add_argument("--account_key")
parser.add_argument("--bucket")
parser.add_argument("--fname")
parser.add_argument("-x")
args = parser.parse_args()

p = ThreadPool(64)
res = []
for i in range(100):
	param = dict(vars(args))
	param['fname'] = "text/5nodes/rankings/part-{}".format(str(i).zfill(5))
	res.append(p.apply_async(scan_file, args=(param,)))

nres = []
for i in res:
	nres.append(i.get())

p.close()
p.join()

with open("result.log", "w") as f:
	json.dump(nres, f)
