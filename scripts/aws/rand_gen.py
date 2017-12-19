from random import randint
import numpy as np

def rand_write(fname):
    rn = rand_gen()
    with open(fname, "w") as f:
        np.save(f, rn, allow_pickle=False)

def rand_read(fname):
    with open(fname, "r") as f:
        res = np.load(f)

    return res

def rand_gen():
    rand_numbers = np.concatenate([np.random.randint(1, 4, size=50), \
        np.random.randint(3, 7, size=25), \
        np.random.randint(2, 6, size=25), \
        np.random.randint(6, 10, size=12), \
        np.random.randint(10, 14, size=13), \
        np.random.randint(14, 17, size=12), \
        np.random.randint(17, 20, size=13), \
        np.random.randint(20, 25, size=10), \
        np.random.randint(20, 30, size=15), \
        np.random.randint(35, 50, size=25), \
        np.random.randint(40, 55, size=25), \
        np.random.randint(20, 30, size=25), \
        np.random.randint(25, 35, size=25), \
        np.random.randint(35, 45, size=25), \
        np.random.randint(50, 65, size=25), \
        np.random.randint(40, 50, size=15), \
        np.random.randint(30, 40, size=15), \
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
        np.random.randint(60, 90, size=10), \
        np.random.randint(70, 90, size=10), \
        np.random.randint(55, 70, size=25)])

    return rand_numbers

