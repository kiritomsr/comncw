from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
from scapy.layers.inet6 import IPv6
from ipaddress import ip_address, IPv6Address, ip_network
from socket import IPPROTO_TCP
import sys
import matplotlib.pyplot as plt
import binascii


class Flow(object):
    def __init__(self, data):
        self.pkts = 0
        self.flows = 0
        self.ft = {}
        for pkt, metadata in RawPcapReader(data):
            self.pkts += 1
            ether = Ether(pkt)
            # print(ether.__repr__())
            # print(metadata)
            if ether.type == 0x86dd:
                ip = ether[IPv6]
                #
                # write your code here
                #
                if not ip.haslayer(TCP):
                    continue
                ip_src_int = int(ip_address(ip.src))
                ip_dst_int = int(ip_address(ip.dst))
                pkt_len = ip.plen

            elif ether.type == 0x0800:
                ip = ether[IP]
                #
                # write your code here
                #
                # print(ip.src)
                # print(ip.dst)
                if not ip.haslayer(TCP):
                    continue
                ip_src_int = int(ip_address(ip.src))
                ip_dst_int = int(ip_address(ip.dst))
                pkt_len = ip.len - ip.ihl * 4

            try:
                tcp = ip[TCP]
            except IndexError as e:
                print(ether.__repr__())
            #
            # write your code here
            #
            pkt_len -= tcp.dataofs * 4
            if pkt_len == 0:
                continue
            recorded = False
            print(ip_address(ip.src))
            print(ip_network(ip.src).network_address)
            for (isi, idi, ts, td) in self.ft:
                if (isi, idi, ts, td) == (ip_src_int, ip_dst_int, tcp.sport, tcp.dport):
                    self.ft[(isi, idi, ts, td)] += pkt_len
                    recorded = True
                    break
                if (idi, isi, td, ts) == (ip_src_int, ip_dst_int, tcp.sport, tcp.dport):
                    self.ft[(isi, idi, ts, td)] += pkt_len
                    recorded = True
                    break

            if not recorded:
                self.ft[(ip_src_int, ip_dst_int, tcp.sport, tcp.dport)] = pkt_len
                self.flows += 1
            # break
        print(self.ft)


if __name__ == '__main__':
    d = Flow(sys.argv[1])
