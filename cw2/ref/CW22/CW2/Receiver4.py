#/*SIYU WANG s1703367*/
import sys
import socket
import math
import time
import struct
import collections


if __name__ == '__main__':
    #read system input
    port = int(sys.argv[1])
    filename = sys.argv[2]
    windows= int(sys.argv[3])
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.bind(('localhost',port))
    recv = [] #received messages
    expack = 0 #expected seqnumber from sender (the first packet's seqnumber in the window)
    buff = [-1] * windows #receiver buffer, initialized to -1
    lastack = 99999999999999999 #last seqnumber, initialized to INF
    while True:
        msg = s.recvfrom(1027)
        bts = list(msg[0])
        file = bytes(bts[3:]) #received 1024 Bytes message
        ack = bts[0]*256 + bts[1] #seqnumber

        if bts[2] == 1: #if EOF is true
            lastack = ack

        if ack == expack: #if received seqnumber is the first packet's seqnumber in the window
            if windows == 1: #"special treatment" when window size is 1
                s.sendto(ack.to_bytes(2, 'big'), msg[1])
                recv.append(file)
                expack+=1
                if expack > lastack:
                    #if last packet is received, send ack 10 times to prevent loss.
                    for i in range(10):
                        s.sendto(ack.to_bytes(2, 'big'), msg[1])
                    break
                continue
            #send seq number as ack to sender
            s.sendto(ack.to_bytes(2,'big'), msg[1])
            try:#if receiver window is not full
                buffed_till = buff[1:].index(-1) # get the index of the next unreceived packet in the window
            except ValueError: # if receiver window is full
                buffed_till = windows-1
            recv.append(file)
            recv += buff[1:buffed_till+1] # put messages from the start of the buffer till next unreceived packet into the recv[]
            #update the buffer, start from the next unreceived paket
            new_buff = buff[buffed_till+1:]
            new_buff += ([-1] * (windows-len(new_buff)))
            buff = new_buff
            expack = ack + 1 + buffed_till #change the value of expack to the seqnumber of the first packet in the window
            if expack > lastack:
                # if last packet is received, send all the ack in the window 10 times to prevent loss.
                for i in range(lastack-windows,expack):
                    for j in range(10):
                        s.sendto(i.to_bytes(2, 'big'), msg[1])
                break
            continue
        if ack != expack:# if received seqnumber is not the seqnumber of the first packet in the window.
            #send ACK
            s.sendto((ack).to_bytes(2, 'big'), msg[1])
            #if the seqnumber  is smaller than the seqnumber of the first packet in the window, doing nothing.
            if ack > expack: #if the seqnumber is greater than the seqnumber of the first packet in the window
                buff[ack - expack] = file #add the packet to the buffer
            continue

    s.close()
    #write file
    f = open(filename,'wb')
    for v in recv:
        f.write(v)
    f.close()


