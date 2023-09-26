#Sender3.py
#s1820742 Weiyu Tu
#run by:
#python3 Receiver3.py 54321 test_3.jpg & python3 Sender3.py localhost 54321 test.jpg 55 32
import sys
import time
import _thread
from socket import*
class My_Timer:
    timer_on = True
    timer_off = False
    
    def __init__(self,duration):     
        self.switch_state = My_Timer.timer_off
        self.begin = -1
        self.max_time = duration

    def start(self):
        if self.switch_state == My_Timer.timer_off:
            self.switch_state = My_Timer.timer_on
            self.begin = time.time()
        else:
            print("Timer have been Reseted!")
            self.begin = time.time()
    
    def reset(self):
        self.switch_state = My_Timer.timer_off
        self.begin = -1
    
    def check_timeout(self):
        # The timer should first be turned on
        if self.switch_state == My_Timer.timer_on:
            # timeout
            return self.max_time < time.time()-self.begin
        # The timer haven't started yet
        else:
            return False
        
        
class Sender3:    
    def __init__(self, IP, port, filename, retry_Time_Out, windowSize):
        if IP == 'localhost':  # Check IP Address
            IP = '127.0.0.1'
        self.IP = IP
        self.port = int(port)
        self.addr_to = (IP,int(port))
        self.file = filename
        self.timer = My_Timer(int(retry_Time_Out)/1000)
        self.window_Size = int(windowSize)
        self.packet = []
        # Number of times of retransmission
        self.Nret = 0
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        #The base of window
        self.base = 0 
        self.mutex = _thread.allocate_lock()

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
        return size/1024

    def go_back_n_t1(self):
        check_sum = len(self.packet)
        nextseq = 0
        _thread.start_new_thread(self.go_back_n_t2,())
        begin = time.time()
        while self.base < check_sum:
            self.mutex.acquire()
            # Send all the packets in the window
            while nextseq < (self.base + self.window_Size):
                # print('Sending packet', nextseq)
                self.clientSocket.sendto(self.packet[nextseq],(self.IP,self.port))
                nextseq += 1
                # print('Next Sequence is ',nextseq)
                
            # Start the timer
            if not self.timer.switch_state:
                # print('Starting timer')
                self.timer.start()
            # Wait until a timer goes off or we get an ACK
            # self.mutex.release()
            while (not self.timer.check_timeout()) and self.timer.switch_state:
                self.mutex.release()
                # print('Sleeping')
                # Sender's thread2 is waiting for the ACK
                time.sleep(0.01)
                self.mutex.acquire()
                # mutex will be unlocked when propriate ACK is received
            
            if self.timer.check_timeout(): 
                self.Nret += 1
                # print("Timeout! Number of retransmission: ", self.Nret)
                # However, if thread2 does not received the ACK till timeout:
                self.timer.reset()
                # Restart sending packages in this window
                nextseq = self.base
            else:
                # Or the mutex is unlocked!
                self.window_Size = min(self.window_Size, check_sum - self.base)
                # print('Shifting window, window size is %d'%self.window_Size)
                # print('Base is ',self.base)

                
            # Unlock the mutex anyway: 1. received ACK and move to the next; 2.timeout and restart
            self.mutex.release()

        self.clientSocket.close()
        return time.time()-begin
        

    def go_back_n_t2(self):
        check_sum = len(self.packet)
        while True:
            ACK, _ = self.clientSocket.recvfrom(2)
            ACK_order = int.from_bytes(ACK, "big")
            if self.base <= ACK_order:
                self.mutex.acquire()
                self.base = ACK_order + 1
                # print('Shifting base to ',self.base)
                self.timer.reset()
                self.mutex.release()
            if ACK_order == check_sum - 1:
                self.complete = 1
                break

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print('Expected filename as command line argument')
        exit()
    Sender = Sender3(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    size = Sender.openfile()
    period = Sender.go_back_n_t1()
    print(size/period)
