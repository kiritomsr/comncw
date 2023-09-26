import sys
import socket
import time
import threading


class Sender:
    def __init__(self, _r_host, _r_port, _file_name, _retry, _window_size):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (_r_host, _r_port)
        self.file = open(_file_name, 'rb').read()
        self.total = len(self.file)
        self.retry = _retry
        self.window_size = _window_size
        self.base = 0
        self.next = 0
        self.retrans = 0
        self.timer = -1

    def send(self, seq_from, seq_to):

        self.next = seq_to
        self.timer = time.time()
        print("send from: " + str(seq_from) + ', to: ' + str(seq_to))
        for seq in range(seq_from, seq_to):

            if (seq + 1) * 1024 >= self.total:
                eof = 1
                seg = self.file[seq * 1024:]
            else:
                eof = 0
                seg = self.file[seq * 1024:(seq + 1) * 1024]
            pkt = seq.to_bytes(2, 'big') + eof.to_bytes(1, 'big') + seg
            self.sock.sendto(pkt, self.addr)

    def receive(self):

        while not self.timeout():
            rcv, _ = self.sock.recvfrom(2)
            ack = int.from_bytes(rcv, 'big')
            print("rcv ack: " + str(ack))
            if ack >= self.base:
                self.base = ack + 1
                self.slide()
            if self.base * 1024 >= self.total:
                return
        if self.timeout():
            self.retransmit()

    def timeout(self):
        return (time.time() - self.timer) >= self.retry

    def retransmit(self):
        print('timeout: ' + str(self.base))
        self.send(self.base, self.base + self.window_size)
        self.retrans += 1
        self.receive()

    def slide(self):
        if self.next < self.base + self.window_size:
            self.send(self.next, self.base + self.window_size)
        self.receive()

    def gbn(self):
        # main = threading.currentThread()
        # recv = threading.Thread(target=self.receive, args=(main,))
        # recv.start()

        start = time.time()
        self.send(self.base, self.base + self.window_size)
        self.receive()

        self.sock.close()
        end = time.time()
        throughput = self.total / ((end - start) * 1024)
        print(str(self.retrans) + ' ' + str(throughput))
        with open('result.csv', 'a') as fr:
            fr.write(str(self.retrans) + '\t' + str(throughput) + '\n')


if __name__ == '__main__':
    r_host = sys.argv[1]
    r_port = int(sys.argv[2])
    file_name = sys.argv[3]
    retry = int(sys.argv[4]) / 1000
    window_size = int(sys.argv[5])

    sender = Sender(r_host, r_port, file_name, retry, window_size)
    sender.gbn()
