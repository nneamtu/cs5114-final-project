from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from packet_set import *
import threading

match_1 = of.ofp_match()
match_1.in_port = 1
match_1.dl_type = 0x0800
match_1.nw_proto = 6
packet_set_1 = PacketSet(Match(match_1), 1)

match_2 = of.ofp_match()
match_2.in_port = 2
match_2.dl_type = 0x0800
match_2.nw_proto = 6
packet_set_2 = PacketSet(Match(match_2), 1)

class OnOffFirewall():

  def __init__(self, c_id, manager):
    self.c_id = c_id
    self.manager = manager

  def replace_rule(self, old_ps, new_ps):
    self.manager.add_rule(new_ps, [], self.c_id)
    self.manager.send_barrier_request(new_ps.get_dpid(), lambda : self.manager.delete_rule(old_ps, self.c_id)) 

  def drop_from_1(self):
    self.replace_rule(packet_set_1, [], packet_set_2, self.c_id)
    timer = threading.Timer(3.0, self.drop_from_2)
    timer.start()

  def drop_from_2(self):
    self.replace_rule(packet_set_2, [], packet_set_1, self.c_id)
    timer = threading.Timer(3.0, self.drop_from_1)
    timer.start()

  def handle_connection_up(self, event):
    if event.dpid == 1:
      self.manager.add_rule(packet_set_1, [], self.c_id)
      timer = threading.Timer(3.0, self.drop_from_2)
      timer.start()

  def handle_connection_down(self, event):
    pass

  def handle_flow_removed(self, event):
    pass

  def handle_port_status(self, event):
    pass

  def handle_packet_in(self, event):
    return False

  def handle_reserved_packet(self, event):
    pass
