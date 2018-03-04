import marshal
import argparse

parser = argparse.ArgumentParser("Aggregation reducer")
parser.add_argument("--file", nargs="+", help="input mapped files")
args = parser.parse_args()
print (args)
all_data = {}
for i in args.file:
    with open(i, "rb") as f:
        data = marshal.load(f)
        for k,v in data.items():
            if k in all_data:
                all_data[k] += v
            else:
                all_data[k] = v

print (len(all_data))
