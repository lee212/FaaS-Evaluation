import boto3

client = boto3.client("lambda")

def create_function(args):
    res = client.create_function(FunctionName=args['function_name'],
            Runtime=args['runtime'],
            Role=args['role'],
            Handler=args['handler'],
            Code=args['code'],
            Description=args['description'],
            Timeout=args['timeout'],
            MemorySize=args['memory'])
    return res
