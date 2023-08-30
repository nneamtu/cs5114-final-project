from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from match import *
from packet_set import *
import shared as shrd
from util import *
import example_a.proactive_routing as proactive_routing
import example_a.firewall as firewall
import example_b.reactive_routing as reactive_routing
import example_b.load_balancer as load_balancer
import example_c.vlb as vlb
import example_d.no_ssh_vlb as no_ssh_vlb
import example_e.even_host_observer as even_host_observer
import testing.on_off_firewall as on_off_firewall
import testing.observer as observer


class Manager(object):

	def __init__(self):

		core.openflow.addListeners(self)

		example_a_config = [firewall.Firewall(0, self), proactive_routing.ProactiveRouting(1, self, 6)]
		example_b_config = [firewall.Firewall(0, self), load_balancer.LoadBalancer(1, self, 8), reactive_routing.ReactiveRouting(2, self)]
		example_c_config = [vlb.VLB(0, self, 6), proactive_routing.ProactiveRouting(1, self, 6)]
		example_d_config = [no_ssh_vlb.NoSSHVLB(0, self, 6), proactive_routing.ProactiveRouting(1, self, 6)]
		example_e_config = [even_host_observer.EvenHostObserver(0, self, 6), proactive_routing.ProactiveRouting(1, self, 6)]
		
		#replace_rule_test_config = [on_off_firewall.OnOffFirewall(0, self), proactive_routing.ProactiveRouting(1, self, 6)] # uses topo A
		#shared_rule_test_config = [observer.Observer(0, self), proactive_routing.ProactiveRouting(1, self, 6)] # uses topo A

		self.c = example_e_config
		
		# maps sub-controller id to priorities
		self.c_pri = []
		offset = 0
		for i in range(len(self.c)):
			self.c_pri = [offset] + self.c_pri
			rng = 2 + 2 ** i
			offset = rng + offset

		# maps sub-controller id to rules
		self.c_rules = [[] for _ in range(len(self.c))]

		# maps sub-controller id to reservations
		self.c_reservs = [[] for _ in range(len(self.c))]

		self.c_sharable = [[] for _ in range(len(self.c))]
		self.c_shared = [[] for _ in range(len(self.c))]

		self.barrier_reqs = dict()

	def __normal_priority(self, c_id):
		"""
		Returns priority for normal rules for given sub-controller.

		c_id : int
		"""
		return self.c_pri[c_id] + 1

	def __reserved_priority(self, c_id):
		"""
		Returns priority for reservation rules for given sub-controller.

		c_id : int
		"""
		return self.c_pri[c_id]

	def __shared_priority(self, c_id, pri):
		"""
		Returns priority for shared rules for given sub-controller and relative
		priority.

		c_id : int
		pri : int
		"""
		return self.c_pri[c_id] + 2 + pri

	def __reserved_actions(self):
		"""
		Returns actions used for reservation rules.
		"""
		return [of.ofp_action_output(port = of.OFPP_CONTROLLER)]

	def send_packet_out(self, data, actions, dpid):
		"""
		Sends packet containing given data and actions to switch specified by 
		given DPID.

		data : bytes, ethernet, ofp_packet_in
		actions : ofp_action list
		dpid : long
		"""
		msg = of.ofp_packet_out(data = data, actions = actions)
		core.openflow.sendToDPID(dpid, msg)

	def send_barrier_req(self, dpid, callback = None):
		"""
		Sends barrier request to switch specified by given DPID.
		Optionally, registers a callback to be executed when the
		barrier reply is received.

		dpid : int
		callback : function (no arguments)
		"""
		barrier_req = of.ofp_barrier_request()
		xid = barrier_req.xid
		core.openflow.sendToDPID(dpid, barrier_req)
		self.barrier_reqs[xid] = callback

	# normal rules
	
	def add_rule(self, packet_set, actions, c_id):
		"""
		Adds rule with the given match (from packet_set) and actions to 
		the switch specified by packet_set. c_id is the id of the
		calling sub-controller.

		packet_set : PacketSet
		actions : ofp_action list
		c_id : int
		"""
		self.c_rules[c_id].append((packet_set, actions))
		print("rule added by", c_id, ":", packet_set, actions)

		msg = of.ofp_flow_mod(match = packet_set.get_match(), actions = actions, priority = self.__normal_priority(c_id))
		core.openflow.sendToDPID(packet_set.get_dpid(), msg)

		# compute any shared rules with higher-priority sub-controllers
		c_rules = self.c_rules.copy()
		c_rules[c_id] = [(packet_set, actions)]
		for id in range(c_id):
			shared = shrd.compute_shared_rules_from_id(id, c_id, self.c_sharable, c_rules)
			self.__add_shared_rules(shared, id)

	def modify_rule(self, packet_set, actions, c_id):
		"""
		Modifies the rule with the given match (from packet_set) on 
		the switch specified by packet_set. The modified rule will use the
		given actions. c_id is the id of the calling sub-controller. 
		The given match must be exactly the same as in the existing rule on 
		the switch, including wildcarded fields.

		packet_set : PacketSet
		actions : ofp_action list
		c_id : int
		"""
		for (ps, a) in self.c_rules[c_id]:
			if packet_set.eq(ps):
				self.c_rules[c_id].remove((ps, a))
				print("rule removed by", c_id, ":", ps, a)
		self.c_rules[c_id].append((packet_set, actions))
		print("rule added by", c_id, ":", packet_set, actions)

		msg = of.ofp_flow_mod(command = of.OFPFC_MODIFY_STRICT, match = packet_set.get_match(), actions = actions, priority = self.__normal_priority(c_id))
		core.openflow.sendToDPID(packet_set.get_dpid(), msg)

		# recompute any shared rules with higher-priority sub-controllers
		c_rules = self.c_rules.copy()
		c_rules[c_id] = [(packet_set, actions)]
		for id in range(c_id):
			shared = shrd.compute_shared_rules_from_id(id, c_id, self.c_sharable, c_rules)
			self.__modify_shared_rules(shared, id)

	def delete_rule(self, packet_set, c_id):
		"""
		Deletes the rule with the given match (from packet_set) on 
		the switch specified by packet_set. c_id is the id of the
		calling sub-controller. 
		The given match must be exactly the same as in the existing rule on 
		the switch, including wildcarded fields.

		packet_set : PacketSet
		c_id : int
		"""
		removed = []
		for (ps, a) in self.c_rules[c_id]:
			if packet_set.eq(ps):
				removed.append((ps, a))
				self.c_rules[c_id].remove((ps, a))
				print("rule removed by", c_id, ":", ps, a)

		msg = of.ofp_flow_mod(command = of.OFPFC_DELETE_STRICT, match = packet_set.get_match(), priority = self.__normal_priority(c_id))
		core.openflow.sendToDPID(packet_set.get_dpid(), msg)

		# delete any shared rules with higher-priority sub-controllers
		c_rules = self.c_rules.copy()
		c_rules[c_id] = removed
		for id in range(c_id):
			shared = shrd.compute_shared_rules_from_id(id, c_id, self.c_sharable, c_rules)
			self.__delete_shared_rules(shared, id)

	# reserved rules

	def add_reservation(self, packet_set, c_id):
		"""
		Adds reservation rule with the given match (from packet_set) to
		the switch specified by packet_set. c_id is the id of the
		calling sub-controller.

		packet_set : PacketSet
		c_id : int
		"""
		self.c_reservs[c_id].append(packet_set)
		actions = self.__reserved_actions()
		print("reservation added by", c_id, ":", packet_set)

		msg = of.ofp_flow_mod(match = packet_set.get_match(), actions = actions, priority = self.__reserved_priority(c_id))
		core.openflow.sendToDPID(packet_set.get_dpid(), msg)

	def delete_reservation(self, packet_set, c_id):
		"""
		Deletes reservation rule with the given match (from packet_set) from
		the switch specified by packet_set. c_id is the id of the
		calling sub-controller.

		packet_set : PacketSet
		c_id : int
		"""
		for ps in self.c_reservs[c_id]:
			if packet_set.eq(ps):
				self.c_reservs[c_id].remove(ps)
				print("reservation removed by", c_id, ":", ps)
		
		msg = of.ofp_flow_mod(command = of.OFPFC_DELETE_STRICT, match = packet_set.get_match(), priority = self.__reserved_priority(c_id))
		core.openflow.sendToDPID(packet_set.get_dpid(), msg)

	# shared rules

	def add_sharable_rule(self, packet_set, actions, c_id):
		"""
		Adds sharable rule for the given PacketSet and actions. 
		Computes resulting shared rules from this new rule, and installs each
		on the switch specified by packet_set. c_id is the id of the
		calling sub-controller.

		packet_set : PacketSet
		actions : ofp_action list
		c_id : int
		"""
		self.c_sharable[c_id].append((packet_set, actions))
		print("sharable rule added by", c_id, ":", packet_set, actions)

		c_sharable = self.c_sharable.copy()
		c_sharable[c_id] = [(packet_set, actions)]
		shared = shrd.compute_shared_rules(c_id, c_sharable, self.c_rules)
		
		self.__add_shared_rules(shared, c_id)

	def modify_sharable_rule(self, packet_set, actions, c_id):
		"""
		Modifies sharable rule for the given PacketSet and actions. 
		Computes resulting shared rules from this new rule, and installs each
		on the switch specified by packet_set. c_id is the id of the
		calling sub-controller.
		The given match must be exactly the same as in the existing rule on 
		the switch, including wildcarded fields.

		packet_set : PacketSet
		actions : ofp_action list
		c_id : int
		"""
		for (ps, a) in self.c_sharable[c_id]:
			if packet_set.eq(ps):
				self.c_sharable.remove((ps, a))
				print("sharable rule removed by", c_id, ":", ps, a)

		c_sharable = self.c_sharable.copy()
		c_sharable[c_id] = [(packet_set, actions)]
		shared = shrd.compute_shared_rules(c_id, c_sharable, self.c_rules)
		
		self.__modify_shared_rules(shared, c_id)

	def delete_sharable_rule(self, packet_set, c_id):
		"""
		Removes sharable rule for the given PacketSet. 
		Also removes the shared rules that resulted from the removed rule, 
		and deletes each from the switch specified by packet_set. 
		c_id is the id of the calling sub-controller.
		The given match must be exactly the same as in the existing rule on 
		the switch, including wildcarded fields.

		packet_set : PacketSet
		c_id : int
		"""
		sharable = []
		for (ps, a) in self.c_sharable[c_id]:
			if packet_set.eq(ps):
				sharable.append((ps, a))
				self.c_sharable.remove((ps, a))
				print("sharable rule removed by", c_id, ":", ps, a)
		
		c_sharable = self.c_sharable.copy()
		c_sharable[c_id] = sharable
		shared = shrd.compute_shared_rules(c_id, c_sharable, self.c_rules)

		self.__delete_shared_rules(shared, c_id)

	# shared rules - private helpers

	def __add_shared_rules(self, shared, c_id):
		"""
		Installs given shared rules (for a single sub-controller) on 
		appropriate switches. 
		c_id is the id of the sub-controller that these rules belong to.

		shared : (PacketSet * ofp_action * int) list
		c_id : int
		"""
		for (ps, a, pri) in shared:
			self.c_shared[c_id].append((ps, a, pri))
			print("shared rule computed for", c_id, ":", ps, a, pri)
			msg = of.ofp_flow_mod(match = ps.get_match(), actions = a, priority = self.__shared_priority(c_id, pri))
			core.openflow.sendToDPID(ps.get_dpid(), msg)

	def __modify_shared_rules(self, shared, c_id):
		"""
		Modifies given shared rules (for a single sub-controller) on 
		appropriate switches. 
		c_id is the id of the sub-controller that these rules belong to.
		For each shared rule, the given match must be exactly the same as 
		in the existing rule on the switch, including wildcarded fields.

		shared : (PacketSet * ofp_action * int) list
		c_id : int
		"""
		for (ps, a, pri) in shared:
			for (ps2, a2, pri2) in self.c_shared[c_id]:
				if ps.eq(ps2) and pri == pri2:
					self.c_shared[c_id].remove((ps2, a2, pri2))
					print("shared rule removed for", c_id, ":", ps2, a2, pri2)
			
			print("shared rule computed for", c_id, ":", ps, a, pri)
			msg = of.ofp_flow_mod(command = of.OFPFC_MODIFY_STRICT, match = ps.get_match(), actions = a, priority = self.__shared_priority(c_id, pri))
			core.openflow.sendToDPID(ps.get_dpid(), msg)

	def __delete_shared_rules(self, shared, c_id):
		"""
		Removes given shared rules (for a single sub-controller) on 
		appropriate switches. 
		c_id is the id of the sub-controller that these rules belong to.
		For each shared rule, the given match must be exactly the same as 
		in the existing rule on the switch, including wildcarded fields.

		shared : (PacketSet * ofp_action * int) list
		c_id : int
		"""
		for (ps, _, pri) in shared:
			for (ps2, a2, pri2) in self.c_shared[c_id]:
				if ps.eq(ps2) and pri == pri2:
					self.c_shared[c_id].remove((ps2, a2, pri2))
					print("shared rule removed by", c_id, ":", ps2, a2, pri2)
			
			msg = of.ofp_flow_mod(command = of.OFPFC_DELETE_STRICT, match = ps.get_match(), priority = self.__shared_priority(c_id, pri))
			core.openflow.sendToDPID(ps.get_dpid(), msg)

	
	def _handle_ConnectionUp(self, event):
		for controller in self.c:
		  controller.handle_connection_up(event)

	def _handle_ConnectionDown(self, event):
		for controller in self.c:
		  controller.handle_connection_down(event)

	def _handle_FlowRemoved(self, event):
		for controller in self.c:
		  controller.handle_flow_removed(event)

	def _handle_PortStatus(self, event):
		for controller in self.c:
		  controller.handle_port_status(event)

	def _handle_BarrierIn(self, event):
		xid = event.xid
		if xid in self.barrier_reqs:
			f = self.barrier_reqs[xid]
			if f != None:
				f()
			self.barrier_reqs.pop(xid, None)

	def _handle_PacketIn(self, event):
		# see if this packet belongs to any reservations
		match = of.ofp_match.from_packet(packet = event.parsed, in_port = event.port)
		packet_set = PacketSet(Match(match), event.dpid)
		done = False
		for id in range(len(self.c)):
			for ps in self.c_reservs[id]:
				if packet_set.subset(ps):
					done = self.c[id].handle_reserved_packet(event)
					break 
			if done:
				break
		if done:
			return
		# else, handle packet normally
		for controller in self.c:
			done = controller.handle_packet_in(event)
			if done:
				break
		
def launch():
	core.registerNew(Manager)
