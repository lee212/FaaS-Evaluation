import time
from ibm_botocore.client import Config
import ibm_boto3

def main(params):
	bucket = params['bucket']
	key = params['key']
	cos_credentials = params['credentials']
	auth_endpoint = 'https://iam.bluemix.net/oidc/token'
	service_endpoint = params['service_endpoint']
	s3d_start = time.time()
	cos = ibm_boto3.client('s3',
                         ibm_api_key_id=cos_credentials['apikey'],
                        ibm_service_instance_id=cos_credentials['resource_instance_id'],
                         ibm_auth_endpoint=auth_endpoint,
                         config=Config(signature_version='oauth'),
                         endpoint_url=service_endpoint)
	r=cos.get_object(Bucket=bucket,Key=key)
	body = r['Body'].read()
	s3d_end = time.time()
	result = {"result":{"s3_elapsed": s3d_end - s3d_start } ,
                "params": params}

	print (result)
	return { "message": result }
