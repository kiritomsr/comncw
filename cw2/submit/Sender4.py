# Shuren Miao S2318786
import sys
import socket
import time
import threading

# class Sender to hold global variables
class Sender:
    def __init__(self, _r_host, _r_port, _file_name, _retry, _window_size):
        self.end = -1
        self.start = -1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (_r_host, _r_port)
        self.file = open(_file_name, 'rb').read()
        # the last seq
        self.last = int(len(self.file) / 1024)
        self.retry = _retry
        self.window_size = _window_size
        # next seq wait acked
        self.base = 0
        # sign for close
        self.end = 0
        self.bye = 65535
        # all seq states list:
        # -1 for unsend, 0 for wait ack, 1 for acked
        self.states = [-1]*(self.last+1)
        # all timer list for send time
        self.timers = [-1]*(self.last+1)

    # function to send pkt of seq
    def send(self, seq):
        # check if sender would like to close
        if seq == self.bye:
            pkt = self.bye.to_bytes(2, 'big') + (0).to_bytes(1, 'big') + (0).to_bytes(1024, 'big')
            self.sock.sendto(pkt, self.addr)
            return
        # check if last pkt
        if seq == self.last:
            eof = 1
            seg = self.file[seq * 1024:]
        else:
            eof = 0
            seg = self.file[seq * 1024:(seq + 1) * 1024]
        # concate header with data
        pkt = seq.to_bytes(2, 'big') + eof.to_bytes(1, 'big') + seg
        # mark seq as waiting for ack
        self.states[seq] = 0
        # record send time for timeout
        self.timers[seq] = time.time()
        self.sock.sendto(pkt, self.addr)

    # function to keep listen ack from receiver
    def receive(self):
        while True:
            rcv, _ = self.sock.recvfrom(2)
            ack = int.from_bytes(rcv, 'big')

            # check if receiver ack to close
            if self.base > self.last and ack == self.bye:
                self.end = 1
                break

            # mark seq as acked
            self.states[ack] = 1
            # slide the window
            if ack == self.base:
                seq_to = self.base + self.window_size if self.base + self.window_size < self.last else self.last
                for seq in range(self.base, seq_to+1):
                    if self.states[seq] == 1:
                        self.base = seq + 1
                    else:
                        self.base = seq
                        break

    # check if seq timeout
    def timeout(self, seq):
        return (time.time() - self.timers[seq]) >= self.retry

    # main logic function
    def sr(self):
        # thread for listen ack from receiver
        recv = threading.Thread(target=self.receive)
        recv.start()

        self.start = time.time()

        # loop to send all data
        while self.base <= self.last:
            # limit the boundary
            seq_to = self.base + self.window_size if self.base + self.window_size < self.last else self.last
            for seq in range(self.base, seq_to+1):
                # resend when timeout
                if self.states[seq] == 0 and self.timeout(seq):
                    self.send(seq)
                # check if window is not full
                if self.states[seq] == -1:

                    self.send(seq)

        # send bye to receiver to close
        if self.base > self.last:
            while not self.end:
                time.sleep(0.1)
                self.send(self.bye)

        self.sock.close()
        self.end = time.time()
        throughput = len(self.file) / ((self.end - self.start) * 1024)
        print(str(throughput))


if __name__ == '__main__':
    r_host = sys.argv[1]
    r_port = int(sys.argv[2])
    file_name = sys.argv[3]
    retry = int(sys.argv[4]) / 1000
    window_size = int(sys.argv[5])
    sender = Sender(r_host, r_port, file_name, retry, window_size)
    sender.sr()
