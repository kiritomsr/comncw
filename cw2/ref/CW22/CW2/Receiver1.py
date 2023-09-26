import sys
import socket


class Receiver:
    def __init__(self,port,file_name):
        self.port = port
        self.file = filename
    def receive(self):
        f = open(filename, 'wb')
        localhost = '127.0.0.1'  # type: str
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.bind(localhost,self.port)
        while True:
            bts, addr = s.recvfrom(1027)
            file= bts[3:]
            f.write(file)
            if bts[2] == 1:
                break
        s.close()
        f.close()

if __name__ == '__main__':
    port = int(sys.argv[1])
    filename = sys.argv[2]
    receiver = Receiver(port, filename)
    receiver.receive_file()

