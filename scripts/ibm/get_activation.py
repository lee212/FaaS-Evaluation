import sys
import json
import requests
import os
import argparse

url = 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/_/activations/'
auth_string = os.environ['IBM_OPENWHISK_AUTH_STRING']

def argument_parser():
    parser = argparse.ArgumentParser("IBM OpenWhisk Activation Results")
    parser.add_argument("fname", help="filename to obtain activation ids")
    args = parser.parse_args()
    return args

def collect_activation_ids(fname):
    with open(fname) as f:
        r = json.load(f)

    try:
        actlist = r.keys()
    except:
        actlist = []
        for i in r:
            tmp = i['result'].keys()
            actlist = actlist + list(tmp)

    return actlist

def read_activation_through_rest(actlist):
    actdict = {}
    for i in actlist:
        # curl -H 'Authorization: Basic
        # NTNjNmY5ZDctM2JhYy00YjQ1LWI3N2ItNGVhMDMzYzg5YmUwOmNjTWxnaW5GU1VtZENuNGI0aWwxb0RaMVI2RlRNdm9QNUdtaUdlc3A3d25ucDR4QjdKQjZzUVpFQzBkTlZjclI='
        # -L
        # 'https://openwhisk.ng.bluemix.net/api/v1/namespaces/_/activations/2cd2e85819ba4a9592e85819ba5a957e'
        headers = {'Authorization': auth_string}
        rdata = requests.get(url + i, headers=headers)
        rdict = rdata.json()
        actdict[i] = rdict

    return actdict

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    args = argument_parser()
    actids = collect_activation_ids(args.fname)
    actdict = read_activation_through_rest(actids)
    to_file("{}.activation".format(args.fname), actdict)
