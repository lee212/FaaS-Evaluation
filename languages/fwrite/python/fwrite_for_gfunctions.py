import os
import time
import sys

start = time.time()
rand_size = 1024
fsize = 1024 # 1MiB
fsize = 1024 * 1024 # 1GiB
fsize = 1024 * 100 # 100MiB
fsize = int(sys.argv[1])
msg = (os.urandom(rand_size)*fsize)

start_fwrite = time.time()
with open('/tmp/output_file', 'wb') as f:
        f.write(msg)
end_fwrite = time.time()

elapsed_fwrite = end_fwrite - start_fwrite
elapsed_function = end_fwrite - start

print ("{},{}".format(elapsed_function, elapsed_fwrite))
