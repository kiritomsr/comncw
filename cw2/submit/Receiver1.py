# Shuren Miao S2318786
import sys
import socket


def receiver(r_port, file_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', r_port))
    with open(file_name, 'wb') as f:
        # loop to keep listen
        while True:
            # listen from sender
            pkt, addr = sock.recvfrom(1027)
            # extract data from pkt
            seg = pkt[3:]
            # write to file
            f.write(seg)
            # check eof to end process
            if pkt[2] == 1:
                break

    sock.close()


if __name__ == '__main__':
    r_port = int(sys.argv[1])
    file_name = sys.argv[2]
    receiver(r_port, file_name)
