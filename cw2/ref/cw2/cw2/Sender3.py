import math
import select
import sys
import socket
import time


def sendPacket(seqNum, lastSeqNum, data):
    if seqNum == lastSeqNum:
        EOF = 1
        pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
        pkt.append(EOF)
        pkt.extend(data[seqNum * 1024:])
    else:
        EOF = 0
        pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
        pkt.append(EOF)
        pkt.extend(data[seqNum * 1024: (seqNum+1) * 1024])
    sock.sendto(pkt, (sIP, sPort))


def receiveACK(base):
    sock.settimeout(retryTimeout)
    data, addr = sock.recvfrom(2)
    ackNum = int.from_bytes(data[:2], 'big')
    if base < ackNum:
        return ackNum
    else:
        return receiveACK(base)


sIP = sys.argv[1]
sPort = int(sys.argv[2])
fileName = open(sys.argv[3], 'rb')
retryTimeout = int(sys.argv[4]) / 1000
windowSize = int(sys.argv[5])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)

file = fileName.read()
data = bytearray(file)
data_left = len(data)

seqNum = 0
lastSeqNum = math.ceil((len(data) / 1024) - 1)
retransmission = 0
base = -1

startTime = time.perf_counter()

while True:
    while seqNum - base <= windowSize and seqNum <= lastSeqNum:
        sendPacket(seqNum, lastSeqNum, data)
        seqNum += 1
    try:
        base = receiveACK(base)
    except socket.error as exc:
        seqNum = base + 1
        retransmission += 1
    if base == lastSeqNum:
        break
        # print("transmission complete")

endTime = time.perf_counter()
transTime = endTime - startTime
throughput = len(data) / (transTime * 1024)
print(str(throughput))
sock.close()
