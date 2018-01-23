import json
import argparse
from operator import itemgetter

def argument_parser():
    parser = argparse.ArgumentParser("Generate Pandas Dataframe to display results")
    parser.add_argument("fname", help="result filename")
    args = parser.parse_args()
    return args

def read_file(fname):
    with open(fname) as f:
        res = json.load(f)
        return res

def generate_dataframe(data):

    res = []
    for k, v in data.items():
        f1 = int(v['billed_duration']) # millisecond
        f2 = v['function_results']['params']['invoke_size']
        f3 = v['function_results']['params']['idx']
        f4 = v['function_results']['elapsed_second']
        res.append([f3, f2, f1])

    res.sort(key=itemgetter(0))
    return res

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    args = argument_parser()
    data = read_file(args.fname)
    res = generate_dataframe(data)
    to_file("{}.data".format(args.fname), res)

