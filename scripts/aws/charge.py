import json
import sys
import math

if len(sys.argv) < 4:
    print "file_name mem_size cnt"
    sys.exit()

fname = sys.argv[1]
mem = sys.argv[2]
cnt = sys.argv[3]

with open(fname) as f:
    r = json.load(f)

msec = 0
for i in r:
    loc = i['message'].find("Billed Duration")
    if loc > 0:
        msec += int(i['message'][loc:].split(" ",3)[2])
        print msec

base_price = 0.00001667
per_request = 0.0000002
mem_size = int(mem) / 1024.0

total_price = per_request * int(cnt)
total_price += base_price * mem_size * math.ceil(msec / 1000.0)

print "{} requested for {} milliseconds, total price: {}".format(cnt, msec,
        total_price)
print "Note. base price: {:.8f}, per_request: {:.7f}".format(base_price, per_request)
