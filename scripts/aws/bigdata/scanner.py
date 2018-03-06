import os 
import boto3 
import time 
from os import listdir 
from os.path import isfile, join 
s3 = boto3.resource("s3") 
def lambda_handler(event, context):
    bucket = event['bucket']
    key = event['key']
    x = event["x"]
    fname = os.path.basename(key)
    fpath = "/tmp/" + fname
    s3.Bucket(bucket).download_file(key, fpath)
    with open(fpath) as f:
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
#    mypath = "/tmp" onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return {"result": { "cnt": r_num, "elapsed": elapsed}, "input": {"event":event, "line_count":len(lines)}}
