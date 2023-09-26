import sys
import socket


def receiver(r_port, file_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('127.0.0.1', r_port))
    seq = 0
    with open(file_name, 'wb') as f:
        while True:
            pkt, addr = sock.recvfrom(1027)
            # print(seq)
            sock.sendto(pkt[:2], addr)
            if seq == int.from_bytes(pkt[:2],'big'):
                seg = pkt[3:]
                f.write(seg)
                seq +=1

                if pkt[2] == 1:
                    for i in range(5):
                        sock.sendto(pkt[:2], addr)
                    break

    sock.close()


if __name__ == '__main__':
    r_port = int(sys.argv[1])
    file_name = sys.argv[2]
    receiver(r_port, file_name)
