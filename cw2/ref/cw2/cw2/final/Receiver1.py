#Receiver1.py
#s1820742 Weiyu Tu
import argparse
from socket import *

parser = argparse.ArgumentParser()
parser.add_argument('Port', type=int, help='Port number')
parser.add_argument('Name', help='File name')
args = parser.parse_args()
host = ''  # Check Port Number
port = args.Port
file = args.Name  # Check file

# print("Receiving file from", port, file)
Socket = socket(AF_INET, SOCK_DGRAM,IPPROTO_UDP)
Socket.bind((host, port))
data,_ = Socket.recvfrom(1027)
checksum = 0
with open(file, 'wb') as f:
    while data:
        message = data[3:]
        order = int.from_bytes(data[:2], "big")
        f.write(message)
        if data[2] == 1:
            break
        data,_ = Socket.recvfrom(1027)
        checksum += 1

f.close()
Socket.close()
