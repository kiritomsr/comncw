import sys
import socket
import time

def sender(r_host, r_port, file_name, retry):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (r_host, r_port)

    file = open(file_name, 'rb').read()
    total = len(file)
    seq = 0
    EOF = 0

    retrans = 0
    start = time.time()

    while seq*1024 < total:

        if (seq + 1) * 1024 >= total:
            EOF = 1
            seg = file[seq * 1024:]
        else:
            seg = file[seq * 1024:(seq + 1) * 1024]

        pkt = seq.to_bytes(2, 'big') + EOF.to_bytes(1, 'big') + seg
        sock.sendto(pkt, addr)
        acked = False
        while not acked:
            try:
                sock.settimeout(retry)
                rcv, _ = sock.recvfrom(2)
                ack = int.from_bytes(rcv,'big')
                if ack >= seq:
                    acked = True
                    print(ack)
            except socket.timeout:
                sock.sendto(pkt, addr)
                retrans += 1
        seq += 1

    sock.close()
    end = time.time()
    throughput = total / ((end - start) * 1024)
    print(str(retrans) + ' ' + str(throughput))
    with open('result.csv', 'a') as fr:
        fr.write(str(retry) + '\t' + str(retrans) + '\t' + str(throughput) + '\n')


if __name__ == '__main__':
    r_host = sys.argv[1]
    r_port = int(sys.argv[2])
    file_name = sys.argv[3]
    retry = int(sys.argv[4]) / 1000
    sender(r_host, r_port, file_name, retry)
