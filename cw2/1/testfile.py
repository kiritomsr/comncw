import sys
import socket
import time

file = open('test.jpg', 'rb').read()
total = len(file)
seg = file[0:1024]
print(len(seg))
