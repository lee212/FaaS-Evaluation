import time
from ibm_botocore.client import Config
import ibm_boto3

"""

Sample Param:
{ "credentials": {
  "apikey": "",
  "endpoints": "https://cos-service.bluemix.net/endpoints",
  "iam_apikey_description": "Auto generated apikey during resource-key operation for Instance - crn:v1:bluemix:public:cloud-object-storage:global",
  "iam_apikey_name": "auto-generated-apikey-",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::",
  "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:"
},
"service_endpoint": "s3.us-south.objectstorage.softlayer.net",
"bucket": "bigdata-benchmark",
"key": "pavlo/text/5nodes/rankings/part-00000",
"x": 1000
}


Reference: 
example
https://medium.com/ibm-data-science-experience/working-with-ibm-cloud-object-storage-in-python-fe0ba8667d5f

notebook example
https://dataplatform.ibm.com/analytics/notebooks/v2/ee1d0b44-0fce-4cf6-8545-e1dc961d0668/view?access_token=c0489b861ab65f63be7e3c5ce962003a2a0197660e67ecb140c477c2e11b5fe3

ibm boto3
https://ibm.github.io/ibm-cos-sdk-python/reference/services/s3.html?highlight=upload_file#S3.Client.get_object

Zipping with virtuaenv and __main__.py file
https://console.bluemix.net/docs/openwhisk/openwhisk_actions.html#creating-python-actions
"""

def main(params):
	bucket = params['bucket']
	key = params['key']
	x = int(params['x'])
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
	lines = r['Body'].read().split(b"\n")
	s3d_end = time.time()
	res = []
	t_start = time.time()
	for line in lines:
		try:
			pageURL, pageRank, avgDuration = line.split(b",")
		except:
			continue
		if int(pageRank) > int(x):
			res.append([pageURL, pageRank])

	t_end = time.time()
	r_num = len(res)
	elapsed = t_end - t_start
	result = {"result":{"cnt": r_num, "elapsed":elapsed, "s3_elapsed": s3d_end - s3d_start } ,
                "params": params}

	print (result)
	return { "message": result }
