import os
import json
import time
import tarfile
import hashlib
import urllib
import sys, os.path

work_path = "/local/Temp/"
asb_download_url = 'https://venv.blob.core.windows.net/azure-storage-blob/asb.tar.gz'
asb_venv = work_path + "azure-storage-blob/Lib/site-packages"

# "2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)]"
_urlretrieve = urllib.urlretrieve

# Initial download if venv is not available to load
def download_venv(venv_path, url, fhash=None):
    if not os.path.isdir(venv_path):
        filepath = work_path + os.path.basename(url)
        if not os.path.isfile(filepath):
            _urlretrieve(url, filepath)
        if fhash:
            hstr = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
            if hstr != fhash:
                print 'md5sum is incorrect'
        c = tarfile.open(filepath)
        c.extractall(work_path)
        c.close()
        os.remove(filepath)

venv_start = time.time()
download_venv(asb_venv, asb_download_url)
sys.path.append(asb_venv)
from azure.storage.blob import BlockBlobService
venv_end = time.time()

def scan_file():
    """
        Test run:
        curl -X POST -d "{\"account_name\":None, \"account_key\": None, 
                        \"bucket\": \"pavlo\",\"fname\":
                        \"text/5nodes/rankings/part-00000\",
                        \"x\": 1000}"
                        'https://test.azurewebsites.net/api/HttpTriggerPython31'
        Sample Params:
        {
            "account_name": xxx,
            "account_key": xxx,
            "bucket": "pavlo",
            "fname": "text/5nodes/rankings/part-00000",
            "x": 1000
        }
    """
    #container_name="pavlo"
    #blob_name="text/5nodes/rankings/part-00000"

    s3d_start = time.time()
    postreqdata = json.loads(open(os.environ['req']).read())
    accountname=postreqdata['account_name']
    accountkey=postreqdata['account_key']
    container_name = postreqdata["bucket"]
    blob_name = postreqdata["fname"]
    x = postreqdata['x']

    block_blob_service = BlockBlobService(account_name=accountname, account_key=accountkey) 
    blob = block_blob_service.get_blob_to_bytes(container_name, blob_name)
    lines = blob.content.split(b"\n")
    res = []
    s3d_end = time.time()

    t_start = time.time()
    for line in lines:
        try:
            pageURL, pageRank, avgDuration = line.split(",")
        except:
            continue
        # SELECT pageURL, pageRank FROM rankings WHERE

        # pageRank > X
        if int(pageRank) > int(x):
            res.append([pageURL, pageRank])

    t_end = time.time()

    r_num = len(res)
    elapsed = t_end - t_start

    response = open(os.environ['res'], 'w')
    result = {"result":{"cnt": r_num, "elapsed":elapsed, "s3_elapsed": s3d_end - s3d_start, "venv_elapsed": venv_end - venv_start},
                "params": postreqdata }
    #Log
    print (result)
    response.write(json.dumps(result))
    response.close()

def main():
    scan_file()

main()
