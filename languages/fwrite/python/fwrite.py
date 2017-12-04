import os
import time

start = time.time()
rand_size = 1024
fsize = 1024 # 1MiB
fsize = 1024 * 1024 # 1GiB
fsize = 1024 * 100 # 100MiB
msg = (os.urandom(rand_size)*fsize)

start_fwrite = time.time()
with open('/tmp/output_file', 'wb') as f:
        f.write(msg)
end_fwrite = time.time()

elapsed_fwrite = end_fwrite - start_fwrite
elapsed_function = end_fwrite - start

print elapsed_function, elapsed_fwrite
