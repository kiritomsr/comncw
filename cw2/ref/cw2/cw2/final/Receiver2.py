#Receiver2.py
#s1820742 Weiyu Tu
import sys
from socket import *


class Receiver2:

   received = 0
   Acked_and_wait = 1

   def __init__(self, port, filename):
      self.file = filename
      self.packet = []
      self.serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
      self.serverSocket.bind(("", int(port)))

   def savefile(self):
      order = 0
      with open(self.file, 'wb') as f:
         while True:
            thispacket = self.packet[order]
            EOF = thispacket[0][2]
            f.write(thispacket[0][3:])
            if EOF:
               break
            order+=1
         f.close()

   def rtd2_2_receiver(self):
      sequence = 0
      while True:
         try:
            data, address = self.serverSocket.recvfrom(1027)
            ACK = data[0:2]
            ACK_order = int.from_bytes(data[:2], "big")
            self.serverSocket.sendto(ACK, address)
            if ACK_order == sequence:
               self.packet.append([data])
               sequence += 1
            if data[2]:
               self.serverSocket.settimeout(3)
               continue
         except timeout:
            break
      self.serverSocket.close()
      # print("Receiver close the socket!")


if __name__ == "__main__":
    Receiver = Receiver2(sys.argv[1],sys.argv[2])
    Receiver.rtd2_2_receiver()
    Receiver.savefile()
