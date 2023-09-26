import socket
import sys

rIP = "127.0.0.1"
rPort = int(sys.argv[1])
fileName = sys.argv[2]
windowSize = int(sys.argv[3])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((rIP, rPort))
data = []
cache = [0] * windowSize
prevSeqNum = 0

while True:
    try:
        pkt, addr = sock.recvfrom(1027)
        pkt_back = pkt[0:2]
        curSeqNum = int.from_bytes(pkt[:2], byteorder='big')
        # print("cur",curSeqNum)
        sock.sendto(pkt_back, addr)
        if curSeqNum == prevSeqNum:
            # data.append([pkt])
            cache[0] = pkt
            # print("prev",prevSeqNum)
            while cache[0]:
                data.append([cache[0]])
                cache = cache[1:]
                cache.append(0)
                prevSeqNum += 1
        elif curSeqNum > prevSeqNum:
            # print(curSeqNum-prevSeqNum)
            cache[curSeqNum - prevSeqNum] = pkt
    except socket.timeout:
        break
    if pkt[2]:
        sock.settimeout(1)
with open(fileName, 'wb') as f:
    for i in data:
        EOF = i[0][2]
        f.write(i[0][3:])
        if EOF:
            break
