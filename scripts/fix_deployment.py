import json
import subprocess
from multiprocessing import Pool
import sys

batch_size = 5
deploy_missing = []
deploy_again = []

fdict = {}
repo_url = "https://github.com/lee212/azure-functions-big-data-benchmark.git"

result = sys.argv[1]
flist = sys.argv[2]

with open(flist) as f1:
    flist = json.load(f1)
    for i in flist:
        fdict[i['name']] = i

def delete(nid):
    print "delete {0}".format(nid)
    name = "flops{0}".format(nid)
    try:
        rgroup = fdict[name]['resourceGroup']
    except:
        # Missing 
        return
    # cmd doesn't provide failure or success 
    cmd = "az functionapp deployment source delete " + \
            "--resource-group {0} --name {1}".format(rgroup, name)
    try:
        o = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        print vars(e)
        return e
    return cmd

def deploy(nid):
    print "deploy {0}".format(nid)
    name = "flops{0}".format(nid)
    try:
        rgroup = fdict[name]['resourceGroup']
    except:
        # Missing 
        return
    cmd = ("az functionapp deployment source config " + \
            " --resource-group {0} --branch master --repo-url {1}" + \
            " --manual-integration --name {2}").format(rgroup, repo_url, name)
    try:
        o = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        print vars(e)
        return e
    return cmd

with open(result) as f:
    rdict = json.load(f)
    for k, v in rdict.iteritems():
        if v['result'] == "":
            # Need a deployment, functions might not exist.
            deploy_missing.append(k)
        elif v['result'].find("error") > 0:
            # Errors during the deployment, delete and redeploy
            deploy_again.append(k)

    p = Pool(batch_size)
    res = []
    print "Number of deploy_again: {0}".format(len(deploy_again))
    res = p.map(delete, deploy_again)
    print res
    #p.close()

    print "Number of deploy_missing: {0}".format(len(deploy_missing))
    p2 = Pool(batch_size)
    res2 = []
    res3 = []
    res2 = p2.map(deploy, deploy_missing)
    res3 = p2.map(deploy, deploy_again)
    print res2, res3
    #p2.close()
