import subprocess
import urllib
import os.path
import datetime
import tarfile
import logging
import botocore
import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
base_path = "/tmp/"

def download(url):
    filename = os.path.basename(url)
    urllib.urlretrieve(url, base_path + filename)
    return filename
            
def lambda_handler(event, context):

    start = datetime.datetime.now()
    script = "flops.py"
    init_numpy = False
    if not os.path.isdir('/tmp/condaruntime'):
        logger.info("tmp/condaruntime does not exist")
        init_numpy = True
        s3 = boto3.resource('s3')
        '''
        s3_res = s3.meta.client.get_object(Bucket='ericmjonas-public', Key='pywren.runtime/pywren_runtime-2.7-default.tar.gz')
        condatar_test = tarfile.open(
            mode="r:gz",
            fileobj=WrappedStreamingBody(s3_res['Body'], s3_res['ContentLength']))
        condatar_test.extractall('/tmp/')
        '''
        p1 = subprocess.Popen(['curl', '-s', '-L','https://s3-us-west-2.amazonaws.com/ericmjonas-public/pywren.runtime/pywren_runtime-2.7-default.tar.gz'], stdout=subprocess.PIPE, preexec_fn=os.setsid)
        p2 = subprocess.Popen(['tar', '-xz', '-C','/tmp'], stdin=p1.stdout, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        p1.stdout.close()
        output,err = p2.communicate()
        p2.stdout.close()
        
        #script = download('https://s3.us-east-2.amazonaws.com/lee212-pywren-751/flops.py')
        try:
            s3.Bucket('lee212-pywren-751').download_file(script,"/tmp/"+script)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
        p1=p2=None
        s3 = None
    
    intermediate = datetime.datetime.now()
    r = subprocess.check_output('/tmp/condaruntime/bin/python /tmp/{0} {1} {2}'.format(script,event['number_of_loop'], event['number_of_matrix']).split())
    end = datetime.datetime.now()
    all_ = end - start
    func_ = end - intermediate
    all_elapsed = "{0}.{1}".format(all_.seconds, all_.microseconds)
    func_elapsed = "{0}.{1}".format(func_.seconds, func_.microseconds)
    
    logger.info("{},{},{},{},{},{},{}".format(event['cid'], event['number_of_loop'], event['number_of_matrix'],float(r)/1e9, func_elapsed, all_elapsed, init_numpy ))
    return float(r) / 1e9
