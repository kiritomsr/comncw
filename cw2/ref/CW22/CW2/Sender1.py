import sys
import socket
import time
import struct

class Sender:
    def __init__(self, host, port, filename=''):
        self.host = host
        self.port = port
        self.file = filename

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

if __name__ == "__main__":
    s = socket.socket(type=socket.SOCK_DGRAM)
    packet = packets(sys.argv[3])
    remotehost = sys.argv[1]
    port = int(sys.argv[2])
    i = 0
    for each in packet:
        s.sendto(each,(remotehost,port))
        time.sleep(0.01)
        i +=1
    s.close()

