#Receiver3.py
#s1820742 Weiyu Tu

import sys
from socket import*
class Receiver3:
    def __init__(self,port,filename):
        self.file = filename
        self.packet = []
        self.serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.serverSocket.bind(("", int(port)))

    def savefile(self):
        order = 0
        # print('Task load = ',len(self.packet))
        with open(self.file, 'wb') as f:
            while True:
                thispacket = self.packet[order]
                # seq = thispacket[0][:2]
                EOF = thispacket[0][2]
                f.write(thispacket[0][3:])
                # print('Saving the packet of Sequence',seq)
                if EOF:
                    break
                order += 1
        f.close()
        # print(self.file," Saved!")

    
    def go_back_n_receiver(self):
        wait_seq = 0
        while True:
            try:
                # Get the next packet from the sender
                data, address = self.serverSocket.recvfrom(1027)
                ACK = data[0:2]
                ACK_order = int.from_bytes(data[:2], "big")
                if ACK_order == wait_seq:
                    # Send back an ACK
                    self.serverSocket.sendto(ACK, address)
                    self.packet.append([data])
                    wait_seq += 1
                # elif ACK_order < wait_seq:
                else:
                    if wait_seq > 0:
                        self.serverSocket.sendto((wait_seq-1).to_bytes(2, byteorder='big'), address)
                if data[2]:
                    self.serverSocket.settimeout(3)
                    continue
            # For the last ACK packet.
            except timeout:
                break
        self.serverSocket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Expected filename as command line argument')
        exit()
    Receiver = Receiver3(sys.argv[1], sys.argv[2])
    Receiver.go_back_n_receiver()
    Receiver.savefile()