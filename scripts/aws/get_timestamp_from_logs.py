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
    res = { "min": 9999999999999,
            "max": 0,
            "diff": 0,
            "diff_datetime": 0 }

    err = 0
    err_msg = []
    for i in rdata:
        if "ResponseMetadata" in i:
            rid = i["ResponseMetadata"]["RequestId"]
        else:
            #KeyError
            err += 1
            err_msg.append(i)
            continue
        if rid in ldata:
            log_messages = ldata[rid]
        else:
            # KeyError
            err += 1
            err_msg.append(i)
            continue
        ts = [ x['timestamp'] for x in log_messages ]
        res[rid] = ts
        res['min'] = min(min(ts), res['min'])
        res['max'] = max(max(ts), res['max'])

    res["diff"] = res["max"] - res["min"]
    res['error'] = { "cnt": err,
            "msg": err_msg }
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
