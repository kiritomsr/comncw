import sys
import socket
import time

sIP = sys.argv[1]
sPort = int(sys.argv[2])
fileName = open(sys.argv[3], 'rb')
retryTimeout = int(sys.argv[4]) / 1000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = (sIP, sPort)

file = fileName.read()
data = bytearray(file)
data_left = len(data)
seqNum = 0
EOF = 0
retransmission = 0
start = time.perf_counter()

while data_left > 0:
    ackSeqNum = 0
    ackReceivedCorrect = False

    packet = bytearray(seqNum.to_bytes(2, byteorder='big'))
    if data_left <= 1024:
        EOF = 1
    else:
        EOF = 0
    packet.append(EOF)
    if EOF == 0:
        packet.extend(data[seqNum * 1024: (seqNum+1) * 1024])
    else:
        packet.extend(data[seqNum * 1024:])
    sock.sendto(packet, addr)
    while not ackReceivedCorrect:
        try:
            sock.settimeout(retryTimeout)
            ack, clientAddr = sock.recvfrom(2)
            ackSeqNum = int.from_bytes(ack[:2], 'big')
            if ackSeqNum == seqNum:
                ackReceivedCorrect = True
        except socket.timeout:
            sock.sendto(packet, addr)
            # print("retransmission")
            retransmission += 1
    seqNum += 1
    data_left -= 1024
    # print(data_left)

end = time.perf_counter()
transTime = end - start
throughput = len(data) / (transTime * 1024)
print(str(retransmission), str(throughput))
sock.close()
