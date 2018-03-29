from random import randint
import numpy as np
import argparse
import pprint

def rand_write(fname, rn):
    np.savetxt(fname, rn, fmt='%d')

def rand_read(fname):
    res = np.genfromtxt(fname, dtype=int)
    return res

def rand_gen():
    rand_numbers = np.concatenate([
        #np.random.randint(1, 4, size=50), \
        #np.random.randint(3, 7, size=25), \
        #np.random.randint(2, 6, size=25), \
        #np.random.randint(6, 10, size=12), \
        np.random.randint(10, 14, size=13), \
        np.random.randint(14, 17, size=12), \
        np.random.randint(17, 20, size=13), \
        np.random.randint(20, 25, size=10), \
        np.random.randint(20, 30, size=15), \
        np.random.randint(35, 50, size=15), \
        np.random.randint(40, 55, size=13), \
        np.random.randint(20, 30, size=10), \
        np.random.randint(25, 35, size=10), \
        np.random.randint(35, 45, size=10), \
        np.random.randint(50, 65, size=10), \
        np.random.randint(40, 50, size=10), \
        np.random.randint(30, 40, size=10), \
        np.random.randint(25, 35, size=10), \
        np.random.randint(20, 30, size=10), \
        np.random.randint(15, 25, size=10), \
        np.random.randint(25, 35, size=10), \
        np.random.randint(35, 40, size=10), \
        np.random.randint(30, 35, size=10), \
        np.random.randint(25, 30, size=10), \
        np.random.randint(50, 60, size=10), \
        np.random.randint(59, 69, size=10), \
        np.random.randint(65, 79, size=10), \
        np.random.randint(75, 89, size=10), \
        np.random.randint(55, 70, size=10)])

    return rand_numbers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rand Number Generator")
    parser.add_argument('--type', metavar='rtype', default='generate', type=str, help="read|write|generate")
    parser.add_argument("--filename", type=str, help="filename to write" +\
            "or read")
    args = parser.parse_args()
    if args.type == "read":
        pprint.pprint(rand_read(args.filename))
    else:
        rlist = rand_gen()
        print (np.sum(rlist))
        if args.type == "write":
            rand_write(args.filename, rlist)
        else:
            pprint.pprint(rlist)
