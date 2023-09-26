import sys
import socket
import time
import threading

global base
global next
global states

global lock


class Sender:
    def __init__(self, _r_host, _r_port, _file_name, _retry, _window_size):

        self.end = -1
        self.start = -1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (_r_host, _r_port)
        self.file = open(_file_name, 'rb').read()
        self.last = int(len(self.file) / 1024) + 1
        self.retry = _retry
        self.window_size = _window_size
        self.retrans = 0
        global base
        global next
        global states
        global lock
        base = 0
        next = 0
        states = [-1 for i in range(self.last)]

        lock = threading.Lock()

    def send(self, seq):
        # print("send from: " + str(seq_from) + ', to: ' + str(seq_to) + ' at: ' + str(time.time() - self.start))
        # if seq_from >= self.last: seq_from = self.last
        # if seq_to > self.last: seq_to = self.last+1
        # self.next = seq_to

        global states
        global lock

        if seq == self.last:
            eof = 1
            seg = self.file[seq * 1024:]
        else:
            eof = 0
            seg = self.file[seq * 1024:(seq + 1) * 1024]
        pkt = seq.to_bytes(2, 'big') + eof.to_bytes(1, 'big') + seg
        lock.acquire()
        states[seq] = 0
        lock.release()
        print("send: " + str(seq))
        time_send = time.time()
        self.sock.sendto(pkt, self.addr)

        while True:
            if self.timeout(time_send):
                print("resend: " + str(seq))
                time_send = time.time()
                self.sock.sendto(pkt, self.addr)
            lock.acquire()
            if states[seq] == 1:
                lock.release()
                break

    def receive(self):
        global states
        global base
        global lock
        while True:
            if base > self.last:
                # print("-----------------------------------------------------ack: " + str(self.base))
                break
            rcv, _ = self.sock.recvfrom(2)
            ack = int.from_bytes(rcv, 'big')
            print("rcv ack: " + str(ack))
            # lock.acquire()
            # states[ack] = 1
            # lock.release()
            lock.acquire()
            if base < ack < base + self.window_size:
                states[ack] = 1
            elif ack == base:
                update = ack + 1

                states[ack] = 1
                for seq in range(base + 1, base + self.window_size):
                    if states[seq] == 1:
                        update = seq
                    else:
                        break
                base = update + 1
                # main.join()
                print("base: " + str(base))
            lock.release()

    def timeout(self, time_send):
        return (time.time() - time_send) >= self.retry

    def sr(self):
        global base
        global next
        global states
        global lock
        # main = threading.currentThread()
        recv = threading.Thread(target=self.receive)
        recv.start()

        self.start = time.time()

        while True:
            lock.acquire()
            if base > self.last:
                lock.release()
                break

            while True:
                lock.acquire()
                seq_from = next if next <= self.last else self.last
                seq_to = base + self.window_size if base + self.window_size < self.last + 1 else self.last + 1
                lock.release()
                for seq in range(seq_from, seq_to):
                    print("begin: " + str(seq))
                    send_next = threading.Thread(target=self.send, args=(next,))
                    send_next.start()
                    if next < seq_to:
                        next = seq_to

        # lock.acquire()
        # self.send(base, base + self.window_size)
        # lock.release()
        # while self.base <= self.last:
        #     for seq in range(self.base, self.base+self.window_size):
        #         # print("check: " + str(seq) + " in " + str(self.states[seq]))
        #         if self.states[seq] == 0 and self.timeout(seq):
        #             print("timeout: " + str(seq))
        #             self.send(seq, seq+1)
        #             self.retrans += 1
        #         if self.states[seq] == -1:
        #             self.send(seq, seq+1)
        #     if self.base > self.last:
        #         recv.join()
        #         break

        # while not self.timeout():
        #     seq_from = self.next if self.next<=self.last else self.last
        #     seq_to = self.base + self.window_size if self.base + self.window_size < self.last+1 else self.last+1
        #     if seq_from < seq_to and self.next <= self.last:
        #         print('from: ' + str(seq_from) + ' to: ' + str(seq_to))
        #         self.send(seq_from, seq_to)
        #         # recv.join()
        #     if self.base > self.last:
        #         recv.join()
        #         break
        #
        # if self.timeout():
        #     # print('timeout: ' + str(self.base) + ' at: ' + str(time.time() - self.start))
        #     self.send(self.base, self.base + self.window_size)
        #     self.retrans += 1
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
