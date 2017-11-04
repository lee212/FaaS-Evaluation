import boto3
import sys
import json

lgn = sys.argv[1]
c = boto3.client("logs")
r = c.describe_log_streams(logGroupName=lgn)
nt = r['nextToken']
ls = r['logStreams']
all_ls = [] + ls

while nt != "":
    r = c.describe_log_streams(logGroupName=lgn, nextToken=nt)
    try:
        nt = r['nextToken']
    except:
        nt = ""
    ls = r['logStreams']
    all_ls += ls

print "all counted log streams: {}".format(len(all_ls))

cnt = 0
all_e = []
for ls in all_ls:
    if 'firstEventTimestamp' not in ls:
        continue
    lsn = ls['logStreamName']
    rr = c.get_log_events(logGroupName=lgn, logStreamName=lsn,
            startFromHead=True)
    nft = rr['nextForwardToken']
    e = rr['events']
    print lsn, len(e)
    all_e += e
    while len(e) > 0:
        rr = c.get_log_events(logGroupName=lgn, logStreamName=lsn,
                nextToken=nft, startFromHead=True)
        nft = rr['nextForwardToken']
        e = rr['events']
        all_e += e
        print nft, len(e)
    print len(all_e), cnt
    cnt += 1

print "Log streams with valid event messages: {}".format(cnt)
print "All log events: {}".format(all_e)


with open("{}.logs".format(lgn), "w") as f:
    json.dump(all_e, f)

