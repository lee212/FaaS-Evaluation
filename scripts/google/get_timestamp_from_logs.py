import os
import json
import argparse
import datetime

def get_argparse():
    parser = argparse.ArgumentParser("read timestamp from stackdriver log file")
    parser.add_argument("fname", help="stackdriver log filename")
    args = parser.parse_args()
    return args

def read_file(fname):
    with open(fname) as f:
        return json.load(f)

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

def read_timestamp(data):
    res = { "min": None,
            "max": None,
            "diff": None }
    err = 0
    err_msg = []
    # data is list
    for i in data:
        #         "timestamp": "2018-02-26T07:13:46.169000+00:00",
        try:
            t = datetime.datetime.strptime(i['timestamp'][:-6],
                    '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError as e:
            err += 1
            err_msg.append(i)
            continue
        if res['max'] is None:
            res['max'] = t
            res['min'] = t
        res['min'] = min(t, res['min'])
        res['max'] = max(t, res['max'])

    res['diff'] = "{}".format(res['max'] - res['min'])
    res['min'] = "{}".format(res['min'])
    res['max'] = "{}".format(res['max'])
    res['error'] = { "cnt": err,
            "msg": err_msg }
    return res

if __name__ == "__main__":
    args = get_argparse()
    rdata = read_file(args.fname)
    res = read_timestamp(rdata)
    outfname = "{}.{}.log".format(os.path.basename(__file__).split(".")[0],
            ".".join(os.path.basename(args.fname).split(".")[:-1]))
    to_file(outfname, res)

