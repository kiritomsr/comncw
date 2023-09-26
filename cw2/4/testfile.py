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

max1 = b'11111111'
imax1 = int.from_bytes(max1, 'big')
print(imax1)

max2 = (-1).to_bytes(2, "big")
print(max2)

max3 = b'11111110'
imax2 = int.from_bytes(max1, 'big')
print(imax2)

# max2 = imax1.to_bytes(8, "big")
# print(max2)

testi = 999
bytei = testi.to_bytes(2, "big")
