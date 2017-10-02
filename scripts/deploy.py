import json
import subprocess
import time
from multiprocessing.pool import ThreadPool

git_url = "https://github.com/lee212/azure-functions-big-data-benchmark.git"

jdict = {}
start = 2540
end = 3000
batch = 1
wait = 10

def worker(cmd):
    s = time.time()
    print cmd
    output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
    e = time.time() - s
    l = cmd.find("--name")
    name = cmd[l:].split()[1]
    return (name, cmd, output, e)

res = {}

def r(result):
    res[result[0]] = { 'cmd': result[1],
            'output': result[2],
            'elapsed_time': result[3]}

def update_timer():
    with open(".deploy.interval") as f:
        tmp = json.load(f)
        return tmp['wait'], tmp['batch_size']

with open('flist2nd') as f:
    jdata = json.load(f)
    for i in jdata:
        jdict[i['name']] = i

    p = ThreadPool(64)

    for i in range(start, end):
        if i == 300:
            # "Pay-As-You-Go-002"
            sid = "def42a73-553d-42d6-aeba-22ea91dd990b"
            cmd = "az account set -s {0}".format(sid)
            t = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
        elif i == 400:
            # "Pay-As-You-Go-003"
            sid = "d6011ee6-abe2-4c15-8eab-f4fa0749e2c7"
            cmd = "az account set -s {0}".format(sid)
            t = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
        elif i == 500:
            # "Pay-As-You-Go-001"
            sid = "6b3cf2b5-2cc1-4828-b5e0-9f8be72e6e6f"
            cmd = "az account set -s {0}".format(sid)
            t = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)

        name = 'flops'+str(i)
        if name not in jdict:
            continue
        rgroup = jdict[name]['resourceGroup']
        cmd = (("az functionapp deployment source config  --resource-group" + \
                " {0} --branch master --repo-url {1} --manual-integration" + \
                " --debug --name {2}").format(rgroup, git_url, name))
        wait, batch = update_timer()
        p.apply_async(worker, args=(cmd,), callback=r)
        if i % batch == 0:

            print "time.sleep({0}) between batch {1}".format(wait, batch)
            time.sleep(wait)
   
            try:
                with open("deploy.result.log", "w") as fout:
                    json.dump(res, fout)
            except:
                pass

