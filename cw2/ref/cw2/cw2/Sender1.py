import sys
import socket

sIP = sys.argv[1]
sPort = int(sys.argv[2])
fileName = open(sys.argv[3],'rb')
sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
addr = (sIP, sPort)

file = fileName.read()
data = bytearray(file)
data_left = len(data)
seqNum = 0
EOF = 0
while data_left > 0:
    if data_left > 1024:
        packet = bytearray(seqNum.to_bytes(2, byteorder='big'))
        packet.append(EOF)
        packet.extend(data[seqNum * 1024: (seqNum+1) * 1024])
        sock.sendto(packet, addr)
    else:
        packet = bytearray(seqNum.to_bytes(2, byteorder='big'))
        EOF = 1
        packet.append(EOF)
        packet.extend(data[seqNum * 1024:])
        sock.sendto(packet, addr)
    seqNum += 1
    data_left -= 1024
sock.close()