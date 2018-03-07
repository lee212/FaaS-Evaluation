import os
import json
import logging
import argparse
from google.cloud import logging as g_logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def argument_parser():
    """ e.g.
    python read_stackdriver_logging.py
    cloudfunctions.googleapis.com%2Fcloud-function

    incorrect logname :
    projects/capable-shard-436/logs/cloudfunctions.googleapis.com%2Fcloud-functions
    """
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
    # page_size with a high number is important not to receive quota limit raise
    # error (ReadRequestsPerMinutePerProject) like:
    # 
    # google.gax.errors.RetryError: RetryError(Exception occurred in retry
    # method that was not classified as transient, caused by <_Rendezvous of RPC
    # that terminated with (StatusCode.RESOURCE_EXHAUSTED, Insufficient tokens
    # for quota 'logging.googleapis.com/read_requests' and limit
    # 'ReadRequestsPerMinutePerProject' of service 'logging.googleapis.com' for
    # consumer 'project_number:764086051850'.)>)
    # 
    # https://googlecloudplatform.github.io/google-cloud-python/latest/logging/logger.html#google.cloud.logging.logger.Logger.list_entries
    page_size = 1000

    for i in g_logger.list_entries(page_size=page_size):
        del(i.logger)
        i.timestamp = i.timestamp.isoformat()
        res.append(vars(i))
        if cnt % page_size == 0:
            logger.info("{} entries".format(cnt))
        cnt += 1
    logger.info("final: {} entries".format(cnt))
    return res

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":

    args = argument_parser()
    res = read_log(args.log_name)
    to_file("stackdriver.{}.log".format(args.log_name), res)


