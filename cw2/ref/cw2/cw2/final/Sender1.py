#Sender1.py
#s1820742 Weiyu Tu
# Run by:
# python3 Receiver1.py 54321 test_1.jpg & python3 Sender1.py localhost 54321 test.jpg
import time
from ipaddress import ip_address
import argparse
from socket import*
parser = argparse.ArgumentParser()
parser.add_argument('IP',help='IP address')
parser.add_argument('Port', type=int, help='Port number')
parser.add_argument('Name', help='File name')
args = parser.parse_args()

if args.IP == 'localhost':  # Check IP Address
    args.IP = '127.0.0.1'
try: ip_address(args.IP)
except ValueError: parser.error('IP Address is not recognized')
IP = args.IP # Check the host
port = args.Port  # Check Port Number
file = args.Name  # Check file

Socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
try:   
    f = open(file, "rb")
except IOError:
    print("Cannot open file", file)
chunk = f.read(1024)
next_chunk = f.read(1024)
sequence,EOF = 0,0
head_12 = sequence.to_bytes(2,byteorder='big')
head_3 = EOF.to_bytes(1, byteorder='big')
while next_chunk:
    Socket.sendto(head_12+head_3+chunk,(IP,port)) #[sequence#1][sequence#2][EOF]
    chunk = next_chunk
    next_chunk = f.read(1024)
    sequence += 1
    time.sleep(0.0005)
    head_12 = sequence.to_bytes(2, byteorder='big')
EOF = 1
head_3 = EOF.to_bytes(1, byteorder='big')
Socket.sendto(head_12+head_3+chunk,(IP,port))
f.close()
time.sleep(10)
Socket.close()
