import os
import time
import sys
import cProfile
import itertools

start = time.time()
rand_size = 1024
fsize = 1024 # 1MiB
fsize = 1024 * 1024 # 1GiB
fsize = 1024 * 100 # 100MiB
fsize = int(sys.argv[1])
cnt = int(sys.argv[2])

def gen_message(size_in_kb):
    return os.urandom(rand_size)*size_in_kb

def fwrite_read(msg, cnt):
    '''
    Args:
        msg: binary string to write
        cnt: interation count

    Return:
        elapsed time
    '''
    start_fwrite = time.time()
    for i in range(cnt):
        with open('/tmp/output_file', 'wb', 0) as f:
            f.write(msg)
    end_fwrite = time.time()

    start_fread = time.time()
    for i in range(cnt):
        with open('/tmp/output_file', 'rb') as f:
            f.read()
            '''
            for j in itertools.count():
                ms = f.read(8192)
                if not ms:
                    break
        print j
        '''
    end_fread = time.time()

    elapsed_fwrite = end_fwrite - start_fwrite
    elapsed_fread = end_fread - start_fread
    return (elapsed_fwrite, elapsed_fread)

msg = gen_message(fsize)
elapsed_fwrite, elapsed_fread = fwrite_read(msg, cnt)

elapsed_function = time.time() - start

print ("{},{},{},{}".format(elapsed_function, elapsed_fwrite, (cnt * fsize *
    rand_size / 1048576.0 / elapsed_fwrite), (cnt * fsize * rand_size /
        1048576.0 / elapsed_fread)))
