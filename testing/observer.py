from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
import pox.lib.addresses as adr
from packet_set import *
import util

class Observer():
  
  def __init__(self, c_id, manager):
    self.c_id = c_id
    self.manager = manager

  def handle_connection_up(self, event):
    match = of.ofp_match()
    match.dl_type = 0x0800
    match.nw_proto = 6
    actions = [of.ofp_action_output(port = of.OFPP_CONTROLLER)]
    self.manager.add_sharable_rule(PacketSet(Match(match), event.dpid), actions, self.c_id) 

  def handle_connection_down(self, event):
    pass

  def handle_flow_removed(self, event):
    pass

  def handle_port_status(self, event):
    pass

  def handle_packet_in(self, event):
    flow = util.get_flow_info(event.parsed)
    if flow != None and flow[0] == 6:
        print("Packet observed:", event.parsed)
        return True
    return False

  def handle_reserved_packet(self, event):
    pass
