import sys
import socket
import time

for i in range(0, 4):
    print(i)

start = time.time()
# time.sleep(1)
end = time.time()
print((end - start)*1000)

file = open('test.jpg', 'rb').read()
last = int(len(file) / 1024)
print(last)
print(len(file))
