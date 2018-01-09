import boto3
import sys
import json
import re
import argparse
import logging

logging.basicConfig(level=logging.INFO)
#logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)


class AWSLog:
    conn = boto3.client("logs")

    def __init__(self, name):
        self.logGroupName = name

    def get_log_streams(self):
        log_streams = \
        self.conn.describe_log_streams(logGroupName=self.logGroupName)

        try:
            nt = log_streams['nextToken']
        except KeyError as e:
            nt = ""
        all_log_streams = []
        all_log_streams += log_streams['logStreams']

        while nt != "":
            log_streams = \
            self.conn.describe_log_streams(logGroupName=self.logGroupName,
                    nextToken=nt)
            try:
                nt = log_streams['nextToken']
            except:
                nt = ""
            all_log_streams += log_streams['logStreams']

        logger.info("all counted log streams: {}".format(len(all_log_streams)))
        return all_log_streams

    def get_log_events(self, streams):
        cnt = 0
        events = []
        for stream in streams:
            # Exception for missing or faulty log messages
            if 'firstEventTimestamp' not in stream:
                continue

            lsn = stream['logStreamName']
            le = self.conn.get_log_events(logGroupName=self.logGroupName,
                    logStreamName=lsn, startFromHead=True)
            events += le['events']
            nft = le['nextForwardToken']
            logger.info("{},{}".format(nft, len(le['events'])))

            # For nextForwardToken
            while len(le['events']) > 0:
                le = self.conn.get_log_events(logGroupName=self.logGroupName,
                        logStreamName=lsn, nextToken=nft, startFromHead=True)
                nft = le['nextForwardToken']
                events += le['events']
                logger.info("{},{}".format(nft, len(le['events'])))
            logger.info("{},{}".format(len(events), cnt))
            cnt += 1

        logger.info("# of Log streams with valid event messages: {}".format(cnt))
        logger.info("# of all log events : {}".format(len(events)))
        return events

def to_file(fname, data):
    with open(fname, "w") as f:
        json.dump(data, f, indent=4)

def get_logs(logGroupName):
    aws_logs = AWSLog(logGroupName)
    streams = aws_logs.get_log_streams()
    events = aws_logs.get_log_events(streams)
    default_fname = "{}.logs".format(logGroupName.replace("/",".")[1:])
    to_file(default_fname, events)

def get_expr_from_logs(fname, expr):

    ar = {}
    err = []
    for fname in fnames.split(","):
        with open(fname) as f:
            r = json.load(f)

        for i in r:
            t = \
            re.match(".*([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}).*",
                    i['message'])
            try:
                key = t.group(1)
            except:
                err.append(i)
                continue
            if key in ar:
                ar[key].append(i)
            else:
                ar[key] = [i]
            '''
            if i['message'].find('1024') > 0:
                try:
                    # 21,10,1024,17.4369022563,1.314976,1.315003,False
                    cid, loop, mat_n, gflop, func_elapsed, all_elapsed, init_numpy = i['message'].split("\t")[3].split(",")
                except:
                    pass
                ar[key] = {"cid": cid,
                        "loop": loop,
                        "mat_n": mat_n,
                        "gflop": gflop,
                        "func_elapsed": func_elapsed,
                        "all_elapsed": all_elapsed,
                        "init_numpy": init_numpy,
                        "timestamp": i['timestamp'],
                        "raw": i['message']
                        }
            '''

    to_file(fname +  ".elastic", ar)
    to_file(fname +  ".elastic.err", err)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS CloudWatch Log Program")
    subparsers = parser.add_subparsers(help='sub-command help', dest='sub')

    parser_read = subparsers.add_parser('get', help='get log messages from AWS')
    parser_read.add_argument('logGroupName', type=str, help='e.g.' + 
                            '/aws/lambda/hello-world')

    parser_analyze = subparsers.add_parser('analyze', help='grep a string in' +
            '\'message\'')
    parser_analyze.add_argument('fname', help='log file name to analyze')
    parser_analyze.add_argument('expr', help='exec expression')

    args = parser.parse_args()
    logger.debug(args)
    if args.sub == "get":
        get_logs(args.logGroupName)
    elif args.sub == "analyze":
        get_expr_from_logs(fname, args.expr)


