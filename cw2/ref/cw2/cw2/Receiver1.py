import socket
import sys

rIP = "127.0.0.1"
rPort = int(sys.argv[1])
fileName = sys.argv[2]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((rIP, rPort))
image = bytearray()

while 1:
    data, addr = sock.recvfrom(1027)
    data_seg = data[3:]
    if data[2] == 1:
        break
    for i in data_seg:
        image.append(i)
with open(fileName, 'wb') as f:
    f.write(image)
sock.close()