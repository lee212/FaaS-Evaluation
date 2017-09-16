import os
import json
import sys
import time
import urllib

postreqdata = json.loads(open(os.environ['req']).read())
furl = postreqdata['url']
x = postreqdata['x']

_urlretrieve = urllib.urlretrieve

# Initial download if venv is not available to load
if not os.path.isfile(os.path.basename(furl)):
    url = furl
    filename = os.path.basename(url)          
    _urlretrieve(url, filename)
                    
f = open(filename)
lines = f.readlines()
res = []
t_start = time.time()
for line in lines:
    pageURL, pageRank, avgDuration = line.split(",")
    # SELECT pageURL, pageRank FROM rankings WHERE
    
    # pageRank > X
    if int(pageRank) > int(x):
        res.append([pageURL, pageRank])

t_end = time.time()

r_num = len(res)
elapsed = t_end - t_start

response = open(os.environ['res'], 'w')
response.write("{0}, {1}".format(r_num, elapsed))
response.close()
