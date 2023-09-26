#/*SIYU WANG s1703367*/
import sys
import socket
import math
import time


if __name__ == '__main__':
    port = int(sys.argv[1]) #receiver listening port
    filename = sys.argv[2] #name for received file to save on local
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.bind(('localhost',port))
    recv = [] #received packages
    dup=[] #received sequence number
    while True:
        msg = s.recvfrom(1027)
        bts = list(msg[0]) # current received package
        file = bytes(bts[3:]) # current file(1024 bytes) received from sender
        if (bts[0],bts[1]) not in dup: #if sequence number is not duplicated
            recv.append(file)
            dup.append((bts[0],bts[1]))# add current sequence number to a list

        if bts[2] == 1: # if the package is the last package
            for i in range(10):# send ack of last package 10 times to avoid loss during transmission
                s.sendto(bytes(bts[0:2]), msg[1])
            break
        s.sendto(bytes(bts[0:2]),msg[1])# if the package is not the last, send back the sequence number as ack
    s.close()
    f = open(filename,'wb')#write file
    for each in recv:
        f.write(each)
    f.close()


