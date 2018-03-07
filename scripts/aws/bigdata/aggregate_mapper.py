import os 
import time
#import json
import marshal 
import boto3 
s3 = boto3.resource("s3") 
client = boto3.client("s3") 
def lambda_handler(event, context):
    bucket = event["bucket"]
    key = event["key"]
    okey = event["okey"]
    x = int(event["x"])
    fname = os.path.basename(key)
    fpath = "/tmp/" + fname

    s3get_start = time.time()
    obj = client.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read()
    s3get_end = time.time()
    s3get_elapsed = s3get_end - s3get_start

    temp1 = { str(i).zfill(2) : {} for i in range(10,100) }
    temp2 = { str(i) + "." : {} for i in range(1,10) }
    res = { **temp1, **temp2 }

    t_start = time.time()
    for line in body.split(b'\n'):
        try:
            sourceIP, destURL, visitDate, adRevenue, rest = line.split(b",",4)
        except:
            continue
        # SELECT SUBSTR(sourceIP, 1, X), SUM(adRevenue) FROM uservisits GROUP BY SUBSTR(sourceIP, 1, X)
        k = sourceIP[:x]
        key_id = k.decode()[:2]
        if k in res[key_id]:
            res[key_id][k] += float(adRevenue)
        else:
            res[key_id][k] = float(adRevenue)
    t_end = time.time()
    r_num = len(res)
    elapsed = t_end - t_start

    obucket = event["obucket"]
    s3u_elapsed = 0
    for k, v in res.items():
        kokey = "{}/{}/{}".format(okey, k, fname)
        s3u_start = time.time()
        s3.Bucket(obucket).put_object(Key=kokey, Body=marshal.dumps(v))#json.dumps(res, indent=4))
        s3u_end = time.time()
        s3u_elapsed += s3u_end - s3u_start
    return {"event": event, "result": {"elapsed":elapsed, "cnt": r_num, "s3_get":s3get_elapsed, "s3_upload":s3u_elapsed}}
