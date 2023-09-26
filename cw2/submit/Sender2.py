# Shuren Miao S2318786
import sys
import socket
import time

def sender(r_host, r_port, file_name, retry):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (r_host, r_port)

    file = open(file_name, 'rb').read()
    total = len(file)
    seq = 0

    retrans = 0
    start = time.time()

    # loop to send all data
    while seq*1024 < total:
        # check if last pkt
        if (seq + 1) * 1024 >= total:
            eof = 1
            seg = file[seq * 1024:]
        else:
            eof = 0
            seg = file[seq * 1024:(seq + 1) * 1024]
        # concate header with data
        pkt = seq.to_bytes(2, 'big') + eof.to_bytes(1, 'big') + seg
        sock.sendto(pkt, addr)
        acked = False
        # loop to wait for ack
        while not acked:
            # try to get ack before timeout
            try:
                sock.settimeout(retry)
                rcv, _ = sock.recvfrom(2)
                ack = int.from_bytes(rcv,'big')
                if ack >= seq:
                    acked = True
            # resend when timeout
            except socket.timeout:
                sock.sendto(pkt, addr)
                retrans += 1
        seq += 1

    sock.close()
    end = time.time()
    throughput = total / ((end - start) * 1024)
    print(str(retrans) + ' ' + str(throughput))


if __name__ == '__main__':
    r_host = sys.argv[1]
    r_port = int(sys.argv[2])
    file_name = sys.argv[3]
    retry = int(sys.argv[4]) / 1000
    sender(r_host, r_port, file_name, retry)
