import json
import os
import argparse

def get_argparse():

    parser = argparse.ArgumentParser("Find elapsed time by reading activations,"
            + " start and end")
    parser.add_argument("fname", help="activation logs where start and end " + \
            "included")
    args = parser.parse_args()
    return args

def read_file(fname):
    with open(fname) as f:
        return json.load(f)

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

def elapsed_time(data):
    res = { "min" : 9999999999999,
            "max": 0,
            "diff": 0 }
    # data is dict type
    for k, v in data.items():
        if not 'start' in v:
            continue
        res['min'] = min(v['start'], res['min'])
        res['max'] = max(v['end'], res['max'])

    res['diff'] = res['max'] - res['min']
    return res

if __name__ == "__main__":
    args = get_argparse()
    rdata = read_file(args.fname)
    res = elapsed_time(rdata)
    outfname = "{}.{}.log".format(os.path.basename(__file__).split(".")[0],
            ".".join(os.path.basename(args.fname).split(".")[:-1]))
    to_file(outfname, res)
