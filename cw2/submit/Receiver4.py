# Shuren Miao S2318786
import sys
import socket


def receiver(r_port, file_name, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', r_port))
    # dict for all cached data
    cache = {}
    # seq wait for receive
    base = 0
    # last seq
    last = 0
    # seq for close
    bye = 65535
    # loop to keep listen
    while True:
        # listen from sender
        pkt, addr = sock.recvfrom(1027)
        now_seq = int.from_bytes(pkt[:2], 'big')
        # check if sender want close
        if now_seq == bye:
            for i in range(5):
                sock.sendto(pkt[:2], addr)
            break
        # seq in window, cache
        elif base < now_seq < base + window_size:
            cache[now_seq] = pkt[3:]
            sock.sendto(pkt[:2], addr)
        # seq in previous, discard
        elif now_seq <= base - 1:
            sock.sendto(pkt[:2], addr)
        # seq wait for
        elif now_seq == base:
            cache[now_seq] = pkt[3:]
            sock.sendto(pkt[:2], addr)
            # slide window by update base
            for i in range(base, base + window_size):
                if i in cache:
                    base = i + 1
                else:
                    base = i
                    break
        # check eof to end process
        if pkt[2] == 1:
            last = now_seq

    sock.close()
    # write all cache into file
    with open(file_name, 'wb') as f:
        for i in range(0, last+1):
            if i not in cache: print("loss: " + str(i))
            f.write(cache[i])


if __name__ == '__main__':
    r_port = int(sys.argv[1])
    file_name = sys.argv[2]
    window_size = int(sys.argv[3])
    receiver(r_port, file_name, window_size)
