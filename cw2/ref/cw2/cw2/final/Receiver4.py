#Receiver4.py 
#s1820742 Weiyu Tu
import sys
from socket import*
class Receiver4:
    def __init__(self,port,filename,window_Size):
        self.file = filename
        self.packet = []
        self.window_Size = int(window_Size)
        self.base = 0
        self.window = [False]*self.window_Size
        self.buffer = [None]*self.window_Size
        self.serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.serverSocket.bind(("", int(port)))

    def savefile(self):
        order = 0
        # print('Task load = ',len(self.packet))
        with open(self.file, 'wb') as f:
            while True:
                thispacket = self.packet[order]
                # print(thispacket)
                # print('Saving the packet of Sequence',int.from_bytes(seq,'big')) 
                EOF = thispacket[2]
                f.write(thispacket[3:])
                if EOF == 1:
                    break
                order += 1
        f.close()

    def selective_Repeat_receiver(self):
        # alls = 0
        # els = 0
        while True:
            try:
                data, addr_from = self.serverSocket.recvfrom(1027)
                ACK = data[0:2]
                ACK_order = int.from_bytes(data[:2], "big")
                # print("Receiver has received the ", ACK_order,
                        #   "th packet!")
                # self.base <= ACK_order < self.base + self.window_Size
                if ACK_order < self.base + self.window_Size and self.base <= ACK_order:
                    # packet is valid 
                    self.serverSocket.sendto(ACK, addr_from)
                    # print("Receiver has send the ", ACK_order,
                    #       "th ACK response packet!")
                    self.buffer[ACK_order - self.base] = data
                    if not self.window[ACK_order - self.base]:
                        # print('Yes We Got Fresh Packet!!')
                        self.window[ACK_order - self.base] = True

                    if self.window[0]:
                        a = len(self.packet)
                        # Update the window
                        shift_num = 0
                        if not False in self.window:
                            #All packet in the window are seccussfully committed
                            shift_num = self.window_Size
                            for i in range(self.window_Size):
                                self.packet.append(self.buffer[i])
                            self.window = [False]*self.window_Size
                            self.buffer = [None]*self.window_Size
                            # alls += (shift_num - len(self.packet) + a)

                        else:
                            while self.window[shift_num] == True:
                                self.packet.append(self.buffer[shift_num])
                                shift_num += 1
                            self.window = self.window[shift_num:] + [False]*shift_num
                            self.buffer = self.buffer[shift_num:] + [None]*shift_num
                            # els += shift_num - len(self.packet) + a
                        self.base += shift_num # Update the window capacity
                        shift_num = 0
                        # print('the base is:',self.base)
                        # print('the window is:', )
                        
                elif ACK_order < self.base:
                    # Duplicate packet
                    self.serverSocket.sendto(ACK, addr_from)
                    # print("stale! Receiver has send the ", ACK_order,
                    #       "th ACK response packet!")
                # else:
                    # print("Weird!!!!!!!!!!!!!!!!!!")
                if data[2]:  # EOF
                    self.serverSocket.settimeout(3)
                    continue
    
            except timeout:
                break
        self.serverSocket.close()
        # print(alls,els)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Expected filename as command line argument')
        exit()
    Receiver = Receiver4(sys.argv[1], sys.argv[2],sys.argv[3])
    period = Receiver.selective_Repeat_receiver()
    size = Receiver.savefile()