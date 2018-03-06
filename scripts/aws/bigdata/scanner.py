import os 
import boto3 
import time 
from os import listdir 
from os.path import isfile, join 

client = boto3.client("s3") 

def lambda_handler(event, context):
    bucket = event['bucket']
    key = event['key']
    x = event["x"]
    s3d_start = time.time()
    obj = client.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read()
    s3d_end = time.time()
    t_start = time.time()
    lines = body.split(b'\n')
    del body
    del obj
    res = []
    for line in lines:
        try:
            pageURL, pageRank, avgDuration = line.split(b",")
        except:
            continue
        # SELECT pageURL, pageRank FROM rankings WHERE pageRank > X
        if int(pageRank) > int(x):
            res.append([pageURL, pageRank])
    t_end = time.time()
    r_num = len(res)
    elapsed = t_end - t_start
#    mypath = "/tmp" onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return {"result": { "cnt": r_num, "elapsed": elapsed, "s3d": s3d_end - s3d_start}, "input": {"event":event, "line_count":len(lines)}}
