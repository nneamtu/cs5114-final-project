from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from match import *

def get_src_ip(packet):
  ip = packet.find("ipv4")
  if ip != None:
    return ip.srcip
  return None

def get_flow_info(packet):
  """
  Returns 5-tuple (protocol, srcip, dstip, srcport, dstport) identifying the flow
  that this packet belongs to. If this packet is not a TCP or UDP packet, then
  returns None.

  packet : parsed packet
  """
  ip = packet.find("ipv4")
  if ip != None:
    protocol = None
    srcport = None
    dstport = None
    srcip = ip.srcip
    dstip = ip.dstip
      
    transport = ip.find("tcp")
    if transport != None:
      protocol = ip.protocol
      srcport = transport.srcport
      dstport = transport.dstport
      return (protocol, srcip, dstip, srcport, dstport)
    else:
      transport = ip.find("udp")
      if transport != None:
        protocol = ip.protocol
        srcport = transport.srcport
        dstport = transport.dstport
        return (protocol, srcip, dstip, srcport, dstport)
      else:
        return None
  else:
    return None

def match_of_flow(flow):
  """
  Returns Match that matches all packets in the specified flow.

  flow : (protocol, srcip, dstip, srcport, dstport)
  """
  (protocol, srcip, dstip, srcport, dstport) = flow
  match = of.ofp_match(dl_type=pkt.ethernet.IP_TYPE, nw_proto=protocol, nw_src=srcip, nw_dst=dstip, tp_src=srcport, tp_dst=dstport)
  return Match(match)

def match_of_reverse_flow(flow):
  """
  Returns Match that matches all packets in the reverse direction of
  the specified flow (i.e., the src/dst IP addrs and ports are flipped).

  flow : (protocol, srcip, dstip, srcport, dstport)
  """
  (protocol, srcip, dstip, srcport, dstport) = flow
  match = of.ofp_match(dl_type=pkt.ethernet.IP_TYPE, nw_proto=protocol, nw_src=dstip, nw_dst=srcip, tp_src=dstport, tp_dst=srcport)
  return Match(match)

def port_of_ip(ip):
  """
  Returns int representing the port on the switch to which the host
  using the given IP address is attached. Assumes that 10.0.0.X is
  located at port X.

  ip : IPAddr
  """
  return int(ip.toStr().replace("10.0.0.", ""))

def src_ip_of_flow(flow):
  return flow[1]

def dst_ip_of_flow(flow):
  return flow[2]
