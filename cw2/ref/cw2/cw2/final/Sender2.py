#Sender2.py
#s1820742 Weiyu Tu
#python3 Receiver2.py 54321 test_2.jpg & python3 Sender2.py localhost 54321 test.jpg 25
import sys
import time
from socket import*

class Sender2:
    wait_ACK = 0
    wait_Send = 1

    def __init__(self, IP, port, filename, Retry_Time_Out):
        if IP == 'localhost':  # Check IP Address
            IP = '127.0.0.1'
        self.IP = IP  
        self.port = int(port)
        self.file = filename 
        self.retTime = float(Retry_Time_Out)/1000
        self.packet = []
        self.state = Sender2.wait_Send
        self.Nret= 0 #number of retransmission

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

    def rtd3_sender(self):  
        self.clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        order = 0
        sequence = 0
        start = time.time()
        while True:
            if self.state == Sender2.wait_Send:
                # print("Sender is on wait_Send state! ")
                self.clientSocket.sendto(self.packet[order], (self.IP, self.port))
                # print("Sender has sent the ",order,"th packet!")
                self.state = Sender2.wait_ACK
                # print("Sender is on wait_ACK state! ")
                self.clientSocket.settimeout(self.retTime)
            elif self.state == Sender2.wait_ACK:
                try:
                    tcost = time.time()
                    ACK, _ = self.clientSocket.recvfrom(2)
                    ACK_order = int.from_bytes(ACK, 'big')
                    order = ACK_order + 1
                    # print("Sender has received the ", ACK_order, "th ACK!")
                    # print("While Sender is waiting for the ", sequence, "th ACK!")
                    if ACK_order == sequence:
                        # self.clientSocket.settimeout(None)
                        # print("Yes They Got The Correct File")
                        sequence += 1
                        self.state = Sender2.wait_Send
                        # print("Sender is on wait_Send state! ")
                        if self.packet[order-1][2]:
                            # print("ALL DONE!")
                            break
                    elif ACK_order < sequence:
                        # print("The Correct File is Lost? Let's send the ",
                            #   ACK_order + 1, "th file again!")
                        # self.state = Sender2.wait_Send
                        self.state = Sender2.wait_ACK
                        tcost = time.time() - tcost
                        if self.retTime>tcost:
                            self.clientSocket.settimeout(self.retTime-tcost)
                            continue
                        else:
                            raise timeout
                        
                except timeout:
                    # print("Timeout!. Sending same packet again...")
                    self.clientSocket.sendto(self.packet[order], (self.IP, self.port))
                    self.state = Sender2.wait_ACK
                    self.Nret += 1
                    self.clientSocket.settimeout(self.retTime)
                 
        self.clientSocket.close()
        end = time.time()
        # print('\nConnection is closed. Good Bye!')
        # print('File is sent successfully in %0.3f seconds' % (end - start))
        return (end-start)


if __name__ == "__main__": 
    Sender = Sender2(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    size = Sender.openfile()
    period = Sender.rtd3_sender()
    throughput = size/period
    print(Sender.Nret, throughput)
