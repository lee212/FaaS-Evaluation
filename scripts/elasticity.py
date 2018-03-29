import json
import os
import time
import sys
import time
import argparse
import logging
import numpy as np
# from fcli import utils
import utils
import rand_gen
from aws import invoke as aws_invoke
from azure import invoke as azure_invoke
from google import invoke as google_invoke
from ibm import invoke as ibm_invoke
from aws.get_duration import get_duration

class elasticInvoke(object):

    name = "elasticInvoke"

    logging.basicConfig(level=logging.INFO)
    #logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging.getLogger(__name__)

    interval = 0.2
    cold_start_delay = 0

    invoke = None

    def elastic_invoke(self):
        """ 
        Invoke a function with concurrent numbers in file 
        """

        self.logger.info("concurrency: {}".format(self.args.concurrent))
        rand_numbers = rand_gen.rand_read(self.args.rand_file)

        res = []
        idx = 0
        isize_total = 0
        total_cnt = np.sum(rand_numbers)
        total_len = (np.ndarray(rand_numbers).shape[0])
        for (v), isize in np.ndenumerate(rand_numbers):

            # <class 'numpy.int64'>
            isize = int(isize)
            event = self.args.params
            event["function_name"] = self.args.func_names
            event["invoke_size"] = isize
            event["idx"] = idx
            # Exception
            self.args.isize = isize
            isize_total += isize

            ret = (self.invoke.handler(event, self.args))
            self.logger.info("{} invoked ({}/{} steps) ({}/{} invoked total) and " + \
                    "sleep {}".format(isize, idx, total_len, isize_total,
                        total_cnt, self.args.interval))
            time.sleep(self.args.interval)
            
            res.append({ 'result': ret, 'invoke_size': isize})
            idx += 1
        return res

    def _aws_lwr(self, invoked_list, log_data):
        res = []
        num = 0
        for i in invoked_list:
            i_size = int(i['invoke_size'])
            for j in i['result']:#['response']:
                try:
                    key = j['ResponseMetadata']['RequestId']
                except:
                    self.logger.error("error {}".format(j))
                    continue
                call_date = j['ResponseMetadata']['HTTPHeaders']['date']

                try:
                    rdata = log_data[key]
                except:
                    self.logger.error(key)
                    continue

                # 0 - START, 1- main message, 2- END, 3- REPORT
                msec = get_duration(rdata[3]['message'])
                if msec:
                    tmp = [num, msec, i_size]
                    res.append(tmp)
                num += 1

        self.logger.info("total invocations: {}".format(len(res)))
        return res

    def _google_lwr(self, invoked_list, log_data):
        res = {}
        for i in log_data:
            eid = str(i['labels']['execution_id'])
            if (i["severity"] == "INFO" and 
                    i['payload'].find("function_results") >= 0):
                res[eid] = json.loads(i['payload'])
            elif (i["severity"] == "DEBUG" and 
                    i['payload'].find("Function execution took") >= 0):
                res[eid]['billed_duration'] = i['payload'].split()[3]

        self.logger.info("total invocations: {}".format(len(res)))
        return res

    def log_with_result(self):

        """
            Connects two output files by RequestId.
            This is necessary for event (async) invocation
        """
        invoke_fname = self.args.res_fname
        log_fname = self.args.log_fname
        target = self.args.target

        with open(invoke_fname) as f:
            invoked_list = json.load(f)

        with open(log_fname) as f:
            log_data = json.load(f)

        func = getattr(self, '_{}_lwr'.format(target))
        res = func(invoked_list, log_data)
        return res

    def get_argparse(self):
    
        parser = argparse.ArgumentParser(description="elasticity: function" + \
                " invocation with rand numbers")
        subparsers = parser.add_subparsers(help='sub-command help', dest='sub')

        #
        # Invoke sub parser 
        #
        parser_invoke = subparsers.add_parser('invoke', help='invoke with rand' + \
                ' numbers')
        # function names, params same as invoke.py
        parser_invoke.add_argument('func_names', metavar='fnames', type=str,
                help='Function' + ' name(s) to invoke')
        parser_invoke.add_argument('params', metavar='params', type=str,
                help='parameters' + ' to a function (json)')
        # rand_file, interval only for elastic
        parser_invoke.add_argument("rand_file", type=str, help="rand numbers from a"
                + " text file")
        parser_invoke.add_argument("--interval", metavar="intvl", type=float,
                default=self.interval, help="time gap" + " between invocation, " + 
                "default:{}".format(self.interval))
        parser_invoke.add_argument('--concurrent', action='store_true',
                dest='concurrent', default=False, help='Concurrency'
                + ' concurrent|sequential')

        #
        # Log subparser
        #
        parser_log = subparsers.add_parser('log', help='read logs with elasticity' +
                ' results')
        parser_log.add_argument('res_fname', help='result file of elastic invoke')
        parser_log.add_argument('log_fname', help='log file')

        for i in [parser, parser_invoke, parser_log]:
            i.add_argument("-t", "--target", help = "target service among: " +  
                    " aws|azure|google|ibm")

        # Google specific parser
        parser_invoke.add_argument('--region', help='region name')
        parser_invoke.add_argument('--project', help='project name')
        parser_invoke.add_argument('--call_type', default="STORAGE", help="trigger type," + 
                " REST|CLI|PUBSUB|STORAGE")
        parser_invoke.add_argument('--option', help="pub/sub topic name or storage bucket"
                + "name depends on call_type")
        args = parser.parse_args()

        self.args = args
        self.parser = parser
        return args

    def gen_filename(self, name, suffix="log"):
        return "{}.{}.elastic_invoked.{}".format(self.name, name, suffix or "")

    def set_provider(self):
        p = self.args.target

        if not p:
            return

        # Invoke function
        # e.g. invoke = aws_invoke # from aws import invoke as aws_invoke
        self.invoke = eval("{}_invoke".format(p))
        
        if p == "google":
            d_project, d_region = google_invoke.config_parser()
            if not self.args.region:
                self.args.region = d_region
            if not self.args.project:
                self.args.project = d_project

    def main(self):
        self.get_argparse()
        self.set_provider()
        args = self.args
        if args.sub == "invoke":
            args.params = json.loads(args.params)
            result = self.elastic_invoke()
            output_fname = self.gen_filename(args.func_names)
        elif args.sub == "log":
            result = log_with_result(args.res_fname, args.log_fname, args.target)
            output_fname = self.gen_filename(args.res_fname, "log.combined")
        else:
            self.parser.print_help()
            sys.exit(-2)

        utils.to_file(output_fname, result)

if __name__ == "__main__":
    elastic = elasticInvoke()
    elastic.main()
