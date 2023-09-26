import socket
import sys

rIP = ""
rPort = int(sys.argv[1])
fileName = sys.argv[2]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((rIP, rPort))
data = []
prevSeqNum = 0

while True:
    pkt, addr = sock.recvfrom(1027)
    curSeqNum = int.from_bytes(pkt[:2], byteorder='big')
    if curSeqNum == prevSeqNum:
        data.append([pkt])
        prevSeqNum += 1
        if pkt[2]:
            pktBack = bytearray(curSeqNum.to_bytes(2, byteorder='big'))
            sock.sendto(pktBack, addr)
            break
    elif curSeqNum < prevSeqNum:
        sock.sendto(pkt[0:2], addr)
with open(fileName, 'wb') as f:
    for i in data:
        EOF = i[0][2]
        f.write(i[0][3:])
        if EOF:
            break
sock.close()