#/*SIYU WANG s1703367*/
import sys
import socket
import math
import time
import struct
import collections

def main(port, filename):
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.bind(('localhost', port))
    recv = [] #create list to store received packets
    expack = 0 #expected ack
    while True:
        msg = s.recvfrom(1027)
        bts = list(msg[0])
        file = bytes(bts[3:])
        ack = bts[0] * 256 + bts[1] #received sequence number from sender

        if bts[2] == 1 and ack == expack: # if the EOF is received and all previous packets have been received
            recv.append(file)
            for i in range(10):
                s.sendto(bytes(bts[0:2]), msg[1]) #send ack multiple times to prevent loss
            break # stop listening port, ready to write file
        if ack == expack: #if received sequence number is expectd and not the last one
            recv.append(file)
            s.sendto(expack.to_bytes(2, 'big'), msg[1]) #send ack to sender
            expack += 1
            continue
        if ack != expack: # if received sequence number is not expected
            #send the last ack number sent to sender
            if expack == 0:
                s.sendto((expack).to_bytes(2, 'big'), msg[1])
            else:
                s.sendto((expack - 1).to_bytes(2, 'big'), msg[1])
            continue

    s.close()
    #write file
    f = open(filename, 'wb')
    for v in recv:
        f.write(v)
    f.close()

if __name__ == '__main__':
    port = int(sys.argv[1])
    filename = sys.argv[2]
    main(port,filename)



