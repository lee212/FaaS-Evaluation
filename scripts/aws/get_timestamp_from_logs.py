import os
import json
import datetime
import argparse

def get_argparse():
    parser = argparse.ArgumentParser(description="read two outputs and find" + \
            " timestamp from requestid")
    parser.add_argument('fname', help="client output file to read requestID")
    parser.add_argument('flname', help="aws log event messages to collect")
    args = parser.parse_args()
    return args

def read_file(fname):
    with open(fname) as f:
        rdata = json.load(f)
        return rdata
def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

def get_timestamp(rdata, ldata):
    1519624219563
    res = { "min": 9999999999999,
            "max": 0,
            "diff": 0,
            "diff_datetime": 0 }
    for i in rdata:
        if "ResponseMetadata" in i:
            rid = i["ResponseMetadata"]["RequestId"]
        else:
            #KeyError
            continue
        if rid in ldata:
            log_messages = ldata[rid]
        else:
            # KeyError
            continue
        ts = [ x['timestamp'] for x in log_messages]
        res[rid] = ts
        res['min'] = min(min(ts), res['min'])
        res['max'] = max(max(ts), res['max'])

    res["diff"] = res["max"] - res["min"]
    return res

if __name__ == "__main__":
    args = get_argparse()
    rdata = read_file(args.fname)
    ldata = read_file(args.flname)
    res = get_timestamp(rdata, ldata)
    ofname = "{}.{}.{}.log".format(os.path.basename(__file__).split(".")[0],
            ".".join(os.path.basename(args.fname).split(".")[:-1]), 
            ".".join(os.path.basename(args.flname).split(".")[:-1]))
    to_file(ofname, res)
