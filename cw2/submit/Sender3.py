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
        # the last seq + 1
        self.last = int(len(self.file)/1024)+1
        self.retry = _retry
        self.window_size = _window_size
        # next seq wait acked
        self.base = 0
        # next seq wait sent
        self.next = 0
        # timer for the newest sent pkt
        self.timer = -1

    # function to send pkt in range
    def send(self, seq_from, seq_to):
        # next pkt to send
        self.next = seq_to
        # timer to record send time
        self.timer = time.time()
        for seq in range(seq_from, seq_to):
            # check if last pkt
            if seq == self.last:
                eof = 1
                seg = self.file[seq * 1024:]
            else:
                eof = 0
                seg = self.file[seq * 1024:(seq + 1) * 1024]
            # concate header with data
            pkt = seq.to_bytes(2, 'big') + eof.to_bytes(1, 'big') + seg
            self.sock.sendto(pkt, self.addr)

    # function to keep listen ack from receiver
    def receive(self):
        while True:
            rcv, _ = self.sock.recvfrom(2)
            ack = int.from_bytes(rcv, 'big')
            # slide the window
            if ack >= self.base:
                self.base = ack
            # check if all acked, return
            if self.base > self.last:
                return

    # check if timeout
    def timeout(self):
        return (time.time() - self.timer) >= self.retry

    # main logic function
    def gbn(self):
        # thread for listen ack from receiver
        recv = threading.Thread(target=self.receive)
        recv.start()

        self.start = time.time()

        # loop to send all data
        while self.base <= self.last:
            # loop to wait for timeout
            while not self.timeout():
                # limit seq boundary
                seq_from = self.next if self.next<=self.last else self.last
                seq_to = self.base + self.window_size if self.base + self.window_size < self.last+1 else self.last+1
                # check if window is not full
                if seq_from < seq_to and self.next <= self.last:
                    self.send(seq_from, seq_to)
                # check if all data acked
                if self.base > self.last:
                    recv.join()
                    break
            # resend when timeout
            if self.timeout():
                self.send(self.base, self.base + self.window_size)

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
    sender.gbn()
