import time
import sys

start = time.time()
time.sleep(float(sys.argv[1]))
end = time.time()
elapsed = end - start

print elapsed
