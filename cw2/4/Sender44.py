#/*SIYU WANG s1703367*/
import sys
import socket
import math
import time
import struct
import os
from threading import Thread,Lock
import queue


class Timer(object):

    def  __init__(self,timeout):
        self.timeout = timeout
        self.start_time = -1

    def start(self):
        if self.start_time == -1:
            self.start_time = time.time()

    def stop(self):
        self.start_time = -1

    def running(self):
        return self.start_time != -1

    def istimeout(self):
        if not self.running():
            return False
        else:
            return (time.time() - self.start_time) > (self.timeout/1000)

#assign port 8888 to sender
SENDER_PORT = 8888

#Use lock for thread safety
lock = Lock()
#2 global variable to share between threads
base = 0
next = 0

#This method is used to parse the input file, split the file to multiple packets with max size 1024 bytes
#then add 3 bytes to the head of each packet. first 2 bytes are sequence number and third byte is EOF.
def packets(filename):
    i = 0
    res = []
    with open(filename,'rb') as f:
        img = f.read(1024)
        while img:
            t = struct.pack(">H", i)
            pre = t + b'\x00'
            pre = pre + img
            res.append(pre)
            img = f.read(1024)

            i+=1
    f.close()
    b = list(res[len(res)-1])
    b[2] = 1
    res[len(res)-1] = bytes(b)
    return res

# Thread for sending a packet
def send_pkt(sock,pkt,seqn,timeout, host,port):

    global acks
    global lock
    timer = Timer(timeout)
    while True:
        if not timer.running() or timer.istimeout(): # If packet has not been sent yet or the packet is timed out,
            timer.stop()                            # restart the timer and send the packet
            sock.sendto(pkt, (host, port))
            timer.start()
            continue
        lock.acquire()
        if not acks[seqn]: #if the packet is not yet acked, wait
            lock.release()
            time.sleep(0.001)
            continue
        else: #if the packet is acked, release the thread
            lock.release()
            break



def send(sock,pkts,windows,timeout,host ,port):
    global acks # a boolean array to indicate if a packet is ACKed.
    global base
    global next
    global lock


    window = windows
    acks = [False]*len(pkts) #initialize to False
    #create and start the ACK receiver's thread
    recv = Thread(target=recv_ack,args=(sock,))
    recv.start()
    while True:
        lock.acquire()
        if base >= len(pkts):# if all packet is sent and acked, release thread
            lock.release()
            break

        #send pkts
        while next < base + window:#while window is not full
            #start thread to send next packet
            sendp = Thread(target=send_pkt,args=(sock,pkts[next],next,timeout,host ,port))
            sendp.start()
            next += 1

        #waiting for the oldest packet being acked
        while not acks[base]:
            lock.release()
            time.sleep(0.00001)
            lock.acquire()

        #When the oldest packet is ACKed, move the window
        base += 1

        pktleft = len(pkts) -base
        if pktleft < windows: #if the number of left packets is smaller than the window
            window = pktleft #set the window size to the number of remaining packets to prevent indexOutOfRange
        else:
            window = windows
        lock.release()

#Thread to receive ACKs
def recv_ack(sock):
    global acks
    global base
    global next
    global lock

    while True:
        if all(acks): # if all packet is ACKed, release thread
            break
        data,_ = sock.recvfrom(1024)
        ack = int.from_bytes(data,'big')
        lock.acquire()
        acks[ack] = True #change the flag of ACKed packet to true.
        lock.release()



if __name__ == "__main__":
    windows = int(sys.argv[5])
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.bind(('localhost',SENDER_PORT))
    #read system inputs
    packet = packets(sys.argv[3])
    remotehost = sys.argv[1]
    port = int(sys.argv[2])
    timeout = int(sys.argv[4])
    #Start transmitting
    startt = time.time()
    send(s,packet,windows,timeout,remotehost,port)

    endt = time.time()
    size = os.path.getsize(sys.argv[3])
    #output result
    print(str(round((size / (1024 * (endt - startt))), 2)))
