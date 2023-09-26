from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import in_proto
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet.tcp import TCP_SYN
from ryu.lib.packet.tcp import TCP_FIN
from ryu.lib.packet.tcp import TCP_RST
from ryu.lib.packet.tcp import TCP_ACK
from ryu.lib.packet.ether_types import ETH_TYPE_IP, ETH_TYPE_ARP

class L4Lb(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L4Lb, self).__init__(*args, **kwargs)
        self.ht = {} # {(<sip><vip><sport><dport>): out_port, ...}
        self.vip = '10.0.0.10'
        self.dips = ('10.0.0.2', '10.0.0.3')
        self.dmacs = ('00:00:00:00:00:02', '00:00:00:00:00:03')
        #
        # write your code here, if needed
        #
        self.cip = '10.0.0.1'
        self.cmac = '00:00:00:00:00:01'


    def _send_packet(self, datapath, port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)
        return out

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        dp = ev.msg.datapath
        ofp, psr = (dp.ofproto, dp.ofproto_parser)
        acts = [psr.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, psr.OFPMatch(), acts)

    def add_flow(self, dp, prio, match, acts, buffer_id=None):
        ofp, psr = (dp.ofproto, dp.ofproto_parser)
        bid = buffer_id if buffer_id is not None else ofp.OFP_NO_BUFFER
        ins = [psr.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, acts)]
        mod = psr.OFPFlowMod(datapath=dp, buffer_id=bid, priority=prio,
                                match=match, instructions=ins)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        in_port, pkt = (msg.match['in_port'], packet.Packet(msg.data))
        dp = msg.datapath
        ofp, psr, did = (dp.ofproto, dp.ofproto_parser, format(dp.id, '016d'))
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        #
        # write your code here, if needed
        #

        iph = pkt.get_protocols(ipv4.ipv4)
        tcph = pkt.get_protocols(tcp.tcp)
        arph = pkt.get_protocol(arp.arp)


        #
        # write your code here
        #

        ### s2318786 begin ###

        if arph:
            # print('handle arp request')
            reply_packet = packet.Packet()
            reply_flag = False
            if arph.dst_ip == self.vip and arph.opcode == arp.ARP_REQUEST:
                src_mac = self.dmacs[0]
                src_ip = self.vip

                reply_packet.add_protocol(ethernet.ethernet(dst=arph.src_mac, src=src_mac, ethertype=ETH_TYPE_ARP))
                reply_packet.add_protocol(arp.arp(opcode=arp.ARP_REPLY, src_mac=src_mac, src_ip=src_ip,
                                         dst_mac=arph.src_mac, dst_ip=arph.src_ip))
                reply_flag = True

            elif arph.dst_ip == self.cip and arph.opcode == arp.ARP_REQUEST:
                src_mac = self.cmac
                src_ip = self.cip

                reply_packet.add_protocol(ethernet.ethernet(dst=arph.src_mac, src=src_mac, ethertype=ETH_TYPE_ARP))
                reply_packet.add_protocol(arp.arp(opcode=arp.ARP_REPLY, src_mac=src_mac, src_ip=src_ip,
                                         dst_mac=arph.src_mac, dst_ip=arph.src_ip))
                reply_flag = True

            if reply_flag:
                reply_packet.serialize()
                actions = [psr.OFPActionOutput(in_port)]
                out = psr.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                                       in_port=in_port, actions=actions, data=reply_packet.data)
                dp.send_msg(out)
                if msg.buffer_id != ofp.OFP_NO_BUFFER:
                    return

        elif iph and tcph:
            # print('handle tcp/ipv4 packet')
            tuple_src = (iph[0].src, iph[0].dst, tcph[0].src_port, tcph[0].dst_port)
            # tuple_dst = (iph[0].dst, iph[0].src, tcph[0].dst_port, tcph[0].src_port)

            if in_port == 1 and iph[0].dst == self.vip:
                if tuple_src not in self.ht:
                    load_port2, load_port3 = 0, 0
                    for tuple in self.ht:
                        if self.ht[tuple] == 2: load_port2 += 1
                        if self.ht[tuple] == 3: load_port3 += 1
                    output_port = 3 if load_port2 > load_port3 else 2
                    self.ht[tuple_src] = output_port
                output_port = self.ht[tuple_src]
                server_dst_ip = self.dips[0] if output_port == 2 else self.dips[1]
                server_dst_mac = self.dmacs[0] if output_port == 2 else self.dmacs[1]
                match = psr.OFPMatch(in_port=in_port, ipv4_src=iph[0].src, ipv4_dst=iph[0].dst,
                                     tcp_src=tcph[0].src_port, tcp_dst=tcph[0].dst_port,
                                     ip_proto=iph[0].proto, eth_type=eth.ethertype)
                actions = [psr.OFPActionSetField(eth_dst=server_dst_mac),
                           psr.OFPActionSetField(ipv4_dst=server_dst_ip),
                           psr.OFPActionOutput(output_port)]
                self.add_flow(dp=dp, prio=1, match=match, acts=actions, buffer_id=msg.buffer_id)
                if msg.buffer_id != ofp.OFP_NO_BUFFER:
                    return
            elif (in_port == 2 or in_port == 3) and iph[0].dst == self.cip:
                output_port = 1
                match = psr.OFPMatch(in_port=in_port, ipv4_src=iph[0].src, ipv4_dst=iph[0].dst,
                                     tcp_src=tcph[0].src_port, tcp_dst=tcph[0].dst_port,
                                     ip_proto=iph[0].proto, eth_type=eth.ethertype)
                actions = [psr.OFPActionSetField(eth_src=self.dmacs[0]),
                           psr.OFPActionSetField(ipv4_src=self.vip),
                           psr.OFPActionOutput(output_port)]
                self.add_flow(dp=dp, prio=1, match=match, acts=actions, buffer_id=msg.buffer_id)
                if msg.buffer_id != ofp.OFP_NO_BUFFER:
                    return
            else:
                out_port = ofp.OFPP_FLOOD
                acts = [psr.OFPActionOutput(out_port)]

        ### s2318786 end ###


        data = msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        out = psr.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                               in_port=in_port, actions=acts, data=data)
        dp.send_msg(out)
