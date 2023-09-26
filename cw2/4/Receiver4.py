import sys
import socket


def receiver(r_port, file_name, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', r_port))
    cache = {}
    base = 0
    last = 0
    bye = 65535

    while True:
        pkt, addr = sock.recvfrom(1027)
        now_seq = int.from_bytes(pkt[:2], 'big')
        print("@@@rcv: " + str(now_seq) + " base: " + str(base))
        if now_seq == bye:
            for i in range(5):
                sock.sendto(pkt[:2], addr)
            break
        elif base < now_seq < base + window_size:
            # print("@@@cache: " + str(now_seq))
            cache[now_seq] = pkt[3:]
            sock.sendto(pkt[:2], addr)
        elif now_seq <= base - 1:
            # print("@@@discard: " + str(now_seq))
            sock.sendto(pkt[:2], addr)
        elif base == now_seq:
            cache[now_seq] = pkt[3:]
            # print("base: " + str(base))
            for i in range(base, base + window_size):
                if i in cache:
                    base = i + 1
                    # print("base: " + str(base))
                else:
                    base = i
                    break
            # print("base: " + str(base))
        if pkt[2] == 1:
            last = now_seq
            print("@@@last: " + str(now_seq))
                # cache[now_seq] = pkt[3:]

            sock.sendto(pkt[:2], addr)

    sock.close()
    with open(file_name, 'wb') as f:
        for i in range(0, last+1):
            if i not in cache: print("loss: " + str(i))
            f.write(cache[i])


if __name__ == '__main__':
    # print("receiver start")
    r_port = int(sys.argv[1])
    file_name = sys.argv[2]
    window_size = int(sys.argv[3])
    receiver(r_port, file_name, window_size)
    # print("receiver end")
