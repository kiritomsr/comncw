from importlib.metadata import metadata
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet.ether_types import ETH_TYPE_IP

class L4State14(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L4State14, self).__init__(*args, **kwargs)
        self.ht = set()

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
        ### s1820742 begin ###
        iph = pkt.get_protocols(ipv4.ipv4)
        tcph = pkt.get_protocols(tcp.tcp)

        out_port = 2 if in_port == 1 else 1
        acts = [psr.OFPActionOutput(out_port)]
        # identify IPV4 packet 
        if iph and tcph:
        # extract the flow key that is a tuple of `(<srcip>, <dstip>, <srcport>, <dstport>)`
            metadata_in = (iph[0].src, iph[0].dst, tcph[0].src_port, tcph[0].dst_port)
            metadata_out = (iph[0].dst, iph[0].src, tcph[0].dst_port, tcph[0].src_port)
            if in_port == 1:
                # illegal combination of TCP flags, which are 
                # 1.) both SYN and FIN set, 
                # 2.) both SYN and RST set or 
                # 3.) no flags are set, it must not forward 
                # those packets nor create the flow in the switch.
                if tcph[0].has_flags(tcp.TCP_SYN, tcp.TCP_RST) or tcph[0].has_flags(tcp.TCP_SYN, tcp.TCP_FIN) or tcph[0].bits == 0:
                    acts = [psr.OFPActionOutput(ofp.OFPPC_NO_FWD)]
                else:
                    if metadata_in not in self.ht:
                        self.ht.add(metadata_in)
                    match = psr.OFPMatch(in_port=in_port,
                                ipv4_src=iph[0].src, ipv4_dst =iph[0].dst, 
                                tcp_dst=tcph[0].dst_port, tcp_src=tcph[0].src_port,
                                ip_proto=iph[0].proto,eth_type=eth.ethertype)
                    acts = [psr.OFPActionOutput(out_port)]
                    self.add_flow(dp=dp, prio=1, match=match, acts=acts, buffer_id=msg.buffer_id)
                    if msg.buffer_id != ofp.OFP_NO_BUFFER:
                        return
            # when the controller sees a returning packet in this TCP connection
            # arriving at switch port 2, it must forward this packet to switch port 1 and insert the
            # corresponding flow to the switch.
            elif in_port == 2: # if coming from 2
                if metadata_out not in self.ht: #if swapped key  (dstip, srcip, dstport, srcport) not in ht
                    acts = [psr.OFPActionOutput(ofp.OFPPC_NO_FWD)] # drop the packet
                else:
                    match = psr.OFPMatch(in_port=in_port, 
                            ipv4_src=iph[0].src, ipv4_dst =iph[0].dst, 
                            tcp_dst=tcph[0].dst_port, tcp_src=tcph[0].src_port,
                            ip_proto=iph[0].proto, eth_type=eth.ethertype)
                    acts = [psr.OFPActionOutput(out_port)] # define the acts
                    self.add_flow(dp=dp, prio=1, match=match, acts=acts, buffer_id=msg.buffer_id)
                    if msg.buffer_id != ofp.OFP_NO_BUFFER: # return
                        return       
            else:
                out_port = ofp.OFPP_FLOOD
                acts = [psr.OFPActionOutput(out_port)]
        ### s1820742 end ###

        data = msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        out = psr.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                               in_port=in_port, actions=acts, data=data)
        dp.send_msg(out)
