#Sender4-3.py
#s1820742 Weiyu Tu
#run by:
#python3 Receiver4.py 54321 test_4.jpg 32 & python3 Sender4-3.py localhost 54321 test.jpg 55 32
import sys
import time
import threading,_thread
from socket import*

class Sender4:
    def __init__(self, IP, port, filename, retry_Time_Out, windowSize):
        if IP == 'localhost':  # Check IP Address
            IP = '127.0.0.1'
        self.addr_to = (IP,int(port))
        self.file = filename
        self.retryTimeOut = int(retry_Time_Out)/1000
        self.window_Size = int(windowSize)
        self.window = [False]*self.window_Size
        self.packet = []
        self.checksum = 0
        self.expect = 0 # number of next expected ACK packat
        self.base = 0  # The base of window
        self.Nret = 0  # Number of times of retransmission
        self.mutex = threading.Lock()
        
    #Load the file into the array of bytes
    def openfile(self):
        f = open(self.file, "rb")
        size = 0
        chunk = f.read(1024)
        next_chunk = f.read(1024)
        sequence, EOF = 0, 0
        head_12 = sequence.to_bytes(2, byteorder='big')
        head_3 = EOF.to_bytes(1, byteorder='big')
        while True:
            if not chunk:
                break
            if not next_chunk:
                EOF = 1
                head_3 = EOF.to_bytes(1, byteorder='big')
            self.packet.append(head_12+head_3+chunk)
            size += 1024
            chunk = next_chunk
            next_chunk = f.read(1024)
            sequence += 1
            head_12 = sequence.to_bytes(2, byteorder='big')
        f.close()
        self.checksum = len(self.packet) # Update the workload
        return size/1024
            
    def selective_Repeat_t1(self):
        # The FSM function 
        begin = time.time()
        while self.expect < self.checksum:
            
            if self.expect < self.base + self.window_Size:
                # One window one thread
                # print('The new thread which has expect order is ',self.expect)
                thread = threading.Thread(target=self.selective_Repeat_t2, args=(self.expect,))
                thread.start()
                self.expect += 1
            # Satisfy the window shifting condition
            if self.window[0]:
                while True:
                    # Can not allow other access when updating the window
                    # Especially the change to the value of base
                    if self.mutex.acquire():
                    # Update the window
                        if not False in self.window:
                            #All packet in the window are seccussfully committed
                            shift_num = self.window_Size
                            self.window = [False]*self.window_Size
                        else:
                            shift_num = 0
                            while self.window[shift_num] == True:
                                shift_num += 1
                            self.window = self.window[shift_num:] + [False]*shift_num
                                
                        # print('new self.window = ',self.window)
                        self.base += shift_num # Update the window capacity
                        shift_num = 0
                        # print('Shifting base to ',self.base)
                        self.mutex.release()
                        break
        return time.time() - begin
        
    def selective_Repeat_t2(self,window_exp):
        #send the packet
        clientSocket = socket(AF_INET,SOCK_DGRAM)
        if window_exp < self.checksum:
            # print('Sending packet', window_exp)
            clientSocket.sendto(self.packet[window_exp], self.addr_to)
        clientSocket.settimeout(self.retryTimeOut)
        while True:
            try:
                ACK ,_= clientSocket.recvfrom(2)
                ACK_order = int.from_bytes(ACK, "big")
                # print('ACK_order received = ', ACK_order)
                
                if ACK_order == window_exp:
                    while True:
                        if self.mutex.acquire():
                        # receive the correct ACK, change the window state and close the socket
                            self.window[ACK_order-self.base] = True
                            # print('The thread which has expect order ',window_exp,'is closed which update the window:',self.window,'from base = ',self.base)
                            self.mutex.release()
                            break
                    clientSocket.close()
                    break
            except timeout:  # time out exception, resend the packet and restart the timer
                self.Nret += 1
                # print("Timeout! Number of retransmission: ", self.Nret)
                clientSocket.sendto(
                    self.packet[window_exp], self.addr_to)
                clientSocket.settimeout(self.retryTimeOut) # reset timer


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print('Expected filename as command line argument')
        exit()
    Sender = Sender4(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    size = Sender.openfile()
    period = Sender.selective_Repeat_t1()
    print(size/period)
