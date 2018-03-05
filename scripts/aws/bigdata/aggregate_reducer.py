import os import time import marshal import boto3 s3 = boto3.resource("s3") client = boto3.client("s3") def lambda_handler(event, context):
    bucket = event["bucket"]
    keys = event["keys"]
    okey = event["okey"]
    prefix = event["prefix"]
    s3d_elapsed = 0
    all_data = {}
    for key in keys:
        fname = os.path.basename(key)
        fpath = "/tmp/" + fname
        s3d_start = time.time()
        obj = client.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read()
        del obj
        s3d_end = time.time()
        s3d_elapsed += (s3d_end - s3d_start)
        data = marshal.loads(body)
        del body
        
        for k, v in data.items():
            if k in all_data:
                all_data[k] += v
            else:
                all_data[k] = v
        del data
    del keys
    
    okey += "".join(prefix.split("/")[-2:])
    s3u_start = time.time()
    s3.Bucket(bucket).put_object(Key=okey, Body=marshal.dumps(all_data)) #json.dumps(all_data, indent=4))
    s3u_end = time.time()
    s3u_elapsed = s3u_end - s3u_start
    r_num = len(all_data)
    res = {"event": event, "result": {"cnt": r_num, "s3_get_object": s3d_elapsed, "s3_put_object":s3u_elapsed}}
    print(res)
    return res
