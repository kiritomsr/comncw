#/*SIYU WANG s1703367*/
import sys
import socket
import math
import time
import struct
import os
from threading import Thread,Lock
import queue


#creat Timer class for the timeout founctinality
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

#4 global variables to share between 2 threads
lock = Lock()
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

def checkleft (w,p,ws):
    result=w
    if p< ws:
        result = p
    else:
        result= ws
    return result

def send(sock,pkts,windows,timeout,host ,port):
    global lastack
    global base
    global next
    global lock
    global timer
  
    timer = Timer(timeout)  # create timer
    window = windows  # window size
    lastpkt = list(pkts[-1])
    lastack = lastpkt[0] * 256 + lastpkt[1]  # expected last ack number from reveiver
    recv = Thread(target=recv_ack, args=(sock,))  # create a Thread for sender to receive ack sent from receiver
    recv.start()
    while True:
        lock.acquire()  # acquire lock for thread safety
        if base >= len(pkts):  # if all packet is sent and acked
            lock.release()
            break

        #send pkts
        while next < base + window:#while window is not full
            sock.sendto(pkts[next],(host,port))#send packet to receiver
            if base == next:
                timer.start()# start timer for the oldest packet
            next += 1

        #waiting
        while timer.running() and not timer.istimeout():  # send process wait until received desired ack
            lock.release()
            time.sleep(0.0001)
            lock.acquire()

        #if timed out
        if timer.istimeout():
            next = base #set the sequence number to the packet number which is not acked and resend the packets in the window
            timer.stop() # stop the timer for new transmission

        window = checkleft(window,len(pkts) -base,windows)
        lock.release()




#method used to receive ack
def recv_ack(sock):
    global lastack
    global base
    global next
    global timer
    global lock

    while True:
        data, _ = sock.recvfrom(1024)
        lock.acquire()  # after received ack from receiver, acquire lock for threas safety
        ack = int.from_bytes(data, 'big')
        base = ack + 1  # move the base to next sequence number
        if base == next:  # if all packet in the current window is sent, stop the timer
            timer.stop()
        if base != next: # if an ACK is received but there are still none ACKed packet, restart timer.
            timer.stop()
            timer.start()
        if ack == lastack:  # if the ack received is the last ack, terminate the thread
            lock.release()
            break
        lock.release()

def main(filename,windows,timeout,remotehost,port):
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.bind(('localhost', SENDER_PORT))
    packet = packets(filename)
    startt = time.time() #start recording transmission time
    send(s, packet, windows, timeout, remotehost, port)
    endt = time.time()
    size = os.path.getsize(filename)
    s.close()
    print(str(round((size / (1024 * (endt - startt))), 2)))#calculate and print the throughput
    return (round((size / (1024 * (endt - startt))), 2))

if __name__ == "__main__":
    # read commandline arguments
    windows = int(sys.argv[5])
    filename = sys.argv[3]
    remotehost = sys.argv[1]
    port = int(sys.argv[2])
    timeout = int(sys.argv[4])
    main(filename,windows,timeout,remotehost,port)

