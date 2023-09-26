import sys
import socket


def sender(r_host, r_port, file_name):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (r_host, r_port)

    file = open(file_name, 'rb').read()
    total = len(file)
    seq = 0
    EOF = 0
    while seq*1024 < total:

        if (seq + 1) * 1024 >= total:
            EOF = 1
            seg = file[seq * 1024:]
        else:
            seg = file[seq * 1024:(seq + 1) * 1024]

        pkt = seq.to_bytes(2, 'big') + EOF.to_bytes(1, 'big') + seg

        sock.sendto(pkt, addr)

        seq += 1

    sock.close()


if __name__ == '__main__':
    r_host = sys.argv[1]
    r_port = int(sys.argv[2])
    file_name = sys.argv[3]
    sender(r_host, r_port, file_name)
