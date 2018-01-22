import os
import json
import logging
import argparse
from google.cloud import logging as g_logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def argument_parser():
    parser = argparse.ArgumentParser("Google Stackdriver Logging Python Client API")
    parser.add_argument("log_name", help="log name which associated with log entries")

    args = parser.parse_args()
    return args

def read_log(log_name):
    g_client = g_logging.Client()
    g_logger = g_client.logger(log_name)

    """
    {'http_request': None, 'logger': <google.cloud.logging.logger.Logger object at
    0x7f0f17074dd8>, 'resource': Resource(type='cloud_function', labels={'region':
    'us-central1', 'project_id': 'capable-shard-436', 'function_name':
    'flops-nodejs-storage'}), 'severity': 'DEBUG', 'payload': "Function execution
    took 572 ms, finished with status: 'ok'", 'labels': {'execution_id':
    '24712273812264'}, 'timestamp': datetime.datetime(2018, 1, 17, 22, 50, 54,
    535915, tzinfo=<UTC>), 'insert_id':
    '000000-76633f89-983a-483b-9674-f432d35da6fd'}
    """

    res = []
    cnt = 0
    for i in g_logger.list_entries():
        del(i.logger)
        i.timestamp = i.timestamp.isoformat()
        res.append(vars(i))
        if cnt == 1000:
            logger.info("{} entries".format(cnt))
        cnt += 1
    return res

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":

    args = argument_parser()
    res = read_log(args.log_name)
    to_file("{}.{}.log".format(os.path.basename(__file__).split(".")[0], args.log_name), res)


