import math
import sys
from socket import *
import threading
import time

sIP = sys.argv[1]
sPort = int(sys.argv[2])
fileName = open(sys.argv[3], 'rb')
timeout = int(sys.argv[4]) / 1000
windowSize = int(sys.argv[5])

file = fileName.read()
data = bytearray(file)
lastSeqNum = math.ceil(len(data)/1024) - 1

base = 0
seqNum = 0
packet_list = {}
acked = {}
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((sIP, sPort+1))


def receiveAck():
    global base
    while True:
        pkt, _ = sock.recvfrom(2)
        ackNum = int.from_bytes(pkt, byteorder='big')
        if ackNum not in acked.keys():
            acked[ackNum] = 1
            while base in acked.keys():
                base += 1

def get_pkt():
    if seqNum == lastSeqNum:
        EOF = 1
        pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
        pkt.append(EOF)
        pkt.extend(data[seqNum * 1024:])
    else:
        EOF = 0
        pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
        pkt.append(EOF)
        pkt.extend(data[seqNum * 1024: (seqNum + 1) * 1024])
    packet_list[seqNum] = pkt

def send_pkt(seqNum):
    while True:
        sock.sendto(packet_list.get(seqNum), (sIP, sPort))
        if acked.get(seqNum) is not None:
            break

thread1 = threading.Thread(target=receiveAck, daemon=True)
thread1.start()
startTime = time.time()

while base < lastSeqNum:
    if seqNum < base + windowSize and seqNum < lastSeqNum + 1:
        get_pkt()
        seq = seqNum
        thread2 = threading.Thread(target=send_pkt, args=[seq], daemon=True)
        thread2.start()
        seqNum += 1

endTime = time.time()
transTime = endTime - startTime
throughput = len(data) / (transTime * 1024)
print(throughput)
