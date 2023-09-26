import sys
import socket
import time
import threading


class Sender:
    def __init__(self, _r_host, _r_port, _file_name, _retry, _window_size):
        self.end = -1
        self.start = -1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (_r_host, _r_port)
        self.file = open(_file_name, 'rb').read()
        self.last = int(len(self.file)/1024)+1
        self.retry = _retry
        self.window_size = _window_size
        self.base = 0
        self.next = 0
        self.retrans = 0
        self.timer = -1

    def send(self, seq_from, seq_to):
        # print("send from: " + str(seq_from) + ', to: ' + str(seq_to) + ' at: ' + str(time.time() - self.start))
        # if seq_from >= self.last: seq_from = self.last
        # if seq_to > self.last: seq_to = self.last+1
        self.next = seq_to
        self.timer = time.time()
        for seq in range(seq_from, seq_to):
            if seq == self.last:
                eof = 1
                seg = self.file[seq * 1024:]
            else:
                eof = 0
                seg = self.file[seq * 1024:(seq + 1) * 1024]
            pkt = seq.to_bytes(2, 'big') + eof.to_bytes(1, 'big') + seg
            self.sock.sendto(pkt, self.addr)

    def receive(self):
        while True:
            rcv, _ = self.sock.recvfrom(2)
            ack = int.from_bytes(rcv, 'big')
            # print("rcv ack: " + str(ack))
            if ack >= self.base:
                self.base = ack
                # main.join()
                # print("base: " + str(self.base))
            if self.base > self.last:
                # print("-----------------------------------------------------ack: " + str(self.base))
                return

    def timeout(self):
        return (time.time() - self.timer) >= self.retry

    def gbn(self):
        # main = threading.currentThread()
        recv = threading.Thread(target=self.receive)
        recv.start()

        self.start = time.time()
        self.send(self.base, self.base + self.window_size)

        while self.base <= self.last:
            while not self.timeout():
                seq_from = self.next if self.next<=self.last else self.last
                seq_to = self.base + self.window_size if self.base + self.window_size < self.last+1 else self.last+1
                if seq_from < seq_to and self.next <= self.last:
                    # print('from: ' + str(seq_from) + ' to: ' + str(seq_to))
                    self.send(seq_from, seq_to)
                    # recv.join()
                if self.base > self.last:
                    recv.join()
                    break

            if self.timeout():
                print('timeout: ' + str(self.base) + ' at: ' + str(time.time() - self.start))
                self.send(self.base, self.base + self.window_size)
                self.retrans += 1
        # time.sleep(0.1)
        self.sock.close()
        self.end = time.time()
        throughput = len(self.file) / ((self.end - self.start) * 1024)
        print(str(throughput))
        with open('result.csv', 'a') as fr:
            fr.write(str(self.window_size) + ':       ' + str(throughput) + '\n')


if __name__ == '__main__':
    r_host = sys.argv[1]
    r_port = int(sys.argv[2])
    file_name = sys.argv[3]
    retry = int(sys.argv[4]) / 1000
    window_size = int(sys.argv[5])
    # print("sender start")
    sender = Sender(r_host, r_port, file_name, retry, window_size)
    sender.gbn()
    # print("sender end")
