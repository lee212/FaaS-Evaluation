import sys
import time
import json

rankings = sys.argv[1]
uservisits = sys.argv[2]
x = sys.argv[3]
date = x

def join_mapper(rankings, uservisits, date):

    datum = {}
    
    t_start = time.time()
    with open(uservisits) as f:
        u_lines = f.readlines()
    """
    with open(rankings) as f:
        r_lines = f.readlines()

    t_end1 = time.time()
    #print t_end1 - t_start
    for line in r_lines:
        pageURL, pageRank, avgDuration = line.split(",")
        datum[pageURL] = { 
                'pageRank': pageRank,
                'userVisits': [] 
                }
    """

    t_end2 = time.time()
    #print t_end2 - t_end1
    for line in u_lines:
        sourceIP, destURL, visitDate, adRevenue, rest = line.split(",",4)
        vdate = time.strptime(visitDate, '%Y-%m-%d')
        if vdate < time.strptime("1980-01-01", '%Y-%m-%d'):
            continue
        if vdate > time.strptime(date, '%Y-%m-%d'):
            continue
        if destURL in datum:
            datum[sourceIP]['adRevenue'] += adRevenue
            datum[sourceIP]['destURL'].append(destURL)
        else:
            datum[sourceIP] = {
                    'destURL': [destURL],
                    'adRevenue': adRevenue
                    }

    t_end3 = time.time()
    print t_end3 - t_end2
    #for k,v in datum.iteritems():
    #    print k,v
    with open("output.json", "w") as f:
        json.dump(datum, f)

def json_reducer(jfile):
    with open(jfile) as f:
        datum = json.load(f)

    res = {}
    #for sourceIP, v in datum.iteritems():


join_mapper(rankings, uservisits, date)
json_reducer('output.json')

