import os
import sys
import zlib
import zipfile
from io import StringIO
import yaml
import argparse

all_providers = ['aws', 'azure', 'google', 'ibm']

def get_argparse():
    parser = argparse.ArgumentParser("FaaS CLI for AWS, Azure, Google, IBM")
    parser.add_argument("-p", "--provider", default=all_providers, 
            help="default: all providers") 
    subparsers = parser.add_subparsers(help="functions command help", dest="cmd")
    parser_create = subparsers.add_parser("create", help="create help")
    parser_create.add_argument("-y", "--yaml", help="Input YAML file containing all"
            + " info e.g. function name, memory size in creating a new"
            + " function")
    args = parser.parse_args()
    # Conver to list by comma 
    if isinstance(args.provider, str):
        args.provider = args.provider.split(",")
    return (parser, args)

def get_yaml(yfname):
    with open(yfname) as f:
        res = yaml.load(f)
        return res

def vendor_filling(provider, args):
    if not os.path.isfile(args['code']):
        inline_code = True
    else:
        inline_code = False

    if provider == "aws":
        # role
        if 'aws_role' in args:
            args['role'] = args['aws_role']
        elif 'aws_role' in os.environ:
            args['role'] = os.environ['aws_role']
        # Code
        if inline_code:
            f = StringIO()
            z = zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED)
            z.writestr('name',args['code'])
            z.clode()
            args['code'] = f.getvalue()
            zip_str = zlib.compress(args['code'].encode('utf-8'))
        else:
            zip_str = open(args['code'], "rb").read()
        args['code'] = {'ZipFile' : zip_str }
        # Runtime
        if args['runtime'] == "nodejs":
            # The runtime parameter of nodejs is no longer supported for
            # creating or updating AWS Lambda functions. We recommend you use
            # the new runtime (nodejs6.10) while creating or updating functions.
            args['runtime'] = "nodejs6.10"
        return args
    elif provider == "azure":
        return args
    elif provider == "google":
        return args
    elif provider == "ibm":
        return args

def _create(args):
    if args.yaml:
        idata = get_yaml(args.yaml)

    for provider in args.provider:
        module_nickname = "{}_{}".format(provider, args.cmd)
        import_exec = ("from {} import {} as {}".format(provider, args.cmd,
            module_nickname))
        exec(import_exec)
        params = vendor_filling(provider, idata)
        func = getattr(eval(module_nickname), "create_function")
        res = func(params)
        print (res)

def main():
    parser, args = get_argparse()
    if args.cmd == None:
        parser.print_help()
        sys.exit(2)
    func = globals()["_" + args.cmd]
    res = func(args)

if __name__ == "__main__":
    main()

