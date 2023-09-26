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
        self.last = int(len(self.file) / 1024)
        self.retry = _retry
        self.window_size = _window_size
        self.retrans = 0
        self.base = 0
        self.end = 0
        self.bye = 65535
        self.states = [-1]*(self.last+1)
        self.timers = [-1]*(self.last+1)

    def send(self, seq):
        if seq == self.bye:
            pkt = self.bye.to_bytes(2, 'big') + (0).to_bytes(1, 'big') + (0).to_bytes(1024, 'big')
            self.sock.sendto(pkt, self.addr)
            return
        if seq == self.last:
            eof = 1
            seg = self.file[seq * 1024:]
            print("send lase " + str(seq))
        else:
            eof = 0
            seg = self.file[seq * 1024:(seq + 1) * 1024]
        pkt = seq.to_bytes(2, 'big') + eof.to_bytes(1, 'big') + seg
        self.states[seq] = 0
        self.timers[seq] = time.time()
        self.sock.sendto(pkt, self.addr)

    def receive(self):
        while True:
            rcv, _ = self.sock.recvfrom(2)
            ack = int.from_bytes(rcv, 'big')
            print("rcv ack: " + str(ack) + " at base: " + str(self.base))

            if self.base > self.last and ack == self.bye:
                self.end = 1
                # print("-----------------------------------------------------ack: " + str(self.base))
                break

            self.states[ack] = 1

            if ack == self.base:
                seq_to = self.base + self.window_size if self.base + self.window_size < self.last else self.last
                for seq in range(self.base, seq_to+1):
                    if self.states[seq] == 1:
                        self.base = seq + 1
                    else:
                        self.base = seq
                        break

                # self.base = ack + 1

                # main.join()
                print("rcv base: " + str(self.base))


    def timeout(self, seq):
        return (time.time() - self.timers[seq]) >= self.retry

    def sr(self):
        # main = threading.currentThread()
        recv = threading.Thread(target=self.receive)
        recv.start()

        self.start = time.time()

        for seq in range(self.base, self.base + self.window_size):
            self.send(seq)

        while self.base <= self.last:

            # seq_from = self.next if self.next<=self.last else self.last
            seq_to = self.base + self.window_size if self.base + self.window_size < self.last else self.last
            for seq in range(self.base, seq_to+1):
                # print("check: " + str(seq))
                if self.states[seq] == 0 and self.timeout(seq):
                    print("timeout: " + str(seq) + " at base: " + str(self.base))
                    self.send(seq)
                    self.retrans += 1
                if self.states[seq] == -1:
                    print("add: " + str(seq) + " at base: " + str(self.base))
                    self.send(seq)

        if self.base > self.last:
            while not self.end:
                print("snd bye")
                time.sleep(0.5)
                self.send(self.bye)
            # recv.join()
            print("rcv byed")

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
    sender.sr()
    # print("sender end")
