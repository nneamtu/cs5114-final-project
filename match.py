from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

class Match(object):
  """
  A Match represents a match on packet header fields, as defined by the
  fields that are matched in OpenFlow. All matches on fields must either
  be exact or wildcards.
  """

  def __init__(self, of_match):
    """
    Requires that of_match includes only exact matches and wildcards
    (no partial matches).
    of_match : ofp_match
    """
    self.m = of_match

  def __str__(self):
    return "Match(" + self.m.__str__() + ")"

  def __repr__(self):
    return "Match(" + self.m.__repr__() + ")"

  def eq(self, other):
    """
    Returns True iff the two matches are equivalent (including wildcarded fields).

    other : Match
    """
    assert isinstance(other, Match)
    return self.m.in_port == other.m.in_port \
      and self.m.dl_src == other.m.dl_src \
      and self.m.dl_dst == other.m.dl_dst \
      and self.m.dl_vlan == other.m.dl_vlan \
      and self.m.dl_vlan_pcp == other.m.dl_vlan_pcp \
      and self.m.dl_type == other.m.dl_type \
      and self.m.nw_tos == other.m.nw_tos \
      and self.m.nw_proto == other.m.nw_proto \
      and self.m.nw_src == other.m.nw_src \
      and self.m.nw_dst == other.m.nw_dst \
      and self.m.tp_src == other.m.tp_src \
      and self.m.tp_dst == other.m.tp_dst

  def subset(self, other):
    """
    Returns True iff this Match matches a subset of packets matched by other 
    (that is, this Match is equivalent to or more specific than other).

    other : Match
    """
    assert isinstance(other, Match)
    return (self.m.in_port == other.m.in_port or other.m.in_port == None) \
      and (self.m.dl_src == other.m.dl_src or other.m.dl_src == None) \
      and (self.m.dl_dst == other.m.dl_dst or other.m.dl_dst == None) \
      and (self.m.dl_vlan == other.m.dl_vlan or other.m.dl_vlan == None) \
      and (self.m.dl_vlan_pcp == other.m.dl_vlan_pcp or other.m.dl_vlan_pcp == None) \
      and (self.m.dl_type == other.m.dl_type or other.m.dl_type == None) \
      and (self.m.nw_tos == other.m.nw_tos or other.m.nw_tos == None) \
      and (self.m.nw_proto == other.m.nw_proto or other.m.nw_proto == None) \
      and (self.m.nw_src == other.m.nw_src or other.m.nw_src == None) \
      and (self.m.nw_dst == other.m.nw_dst or other.m.nw_dst == None) \
      and (self.m.tp_src == other.m.tp_src or other.m.tp_src == None) \
      and (self.m.tp_dst == other.m.tp_dst or other.m.tp_dst == None)

  def overlap(self, other):
    """
    Returns True iff this Match matches a non-empty set of packets that is
    also matched by other.

    other : Match
    """
    assert isinstance(other, Match)
    return (self.m.in_port == other.m.in_port or self.m.in_port == None or other.m.in_port == None) \
      and (self.m.dl_src == other.m.dl_src or self.m.dl_src == None or other.m.dl_src == None) \
      and (self.m.dl_dst == other.m.dl_dst or self.m.dl_dst == None or other.m.dl_dst == None) \
      and (self.m.dl_vlan == other.m.dl_vlan or self.m.dl_vlan == None or other.m.dl_vlan == None) \
      and (self.m.dl_vlan_pcp == other.m.dl_vlan_pcp or self.m.dl_vlan_pcp == None or other.m.dl_vlan_pcp == None) \
      and (self.m.dl_type == other.m.dl_type or self.m.dl_type == None or other.m.dl_type == None) \
      and (self.m.nw_tos == other.m.nw_tos or self.m.nw_tos == None or other.m.nw_tos == None) \
      and (self.m.nw_proto == other.m.nw_proto or self.m.nw_proto == None or other.m.nw_proto == None) \
      and (self.m.nw_src == other.m.nw_src or self.m.nw_src == None or other.m.nw_src == None) \
      and (self.m.nw_dst == other.m.nw_dst or self.m.nw_dst == None or other.m.nw_dst == None) \
      and (self.m.tp_src == other.m.tp_src or self.m.tp_src == None or other.m.tp_src == None) \
      and (self.m.tp_dst == other.m.tp_dst or self.m.tp_dst == None or other.m.tp_dst == None)

  def intersect(self, other):
    """
    Returns a new Match representing the intersection of this Match and other;
    that is, it will match all packets that are matched by this Match and
    by other.

    If this Match and other do not overlap, then returns None.

    other : Match
    """
    if not self.overlap(other):
      return None
    
    m = of.ofp_match()
    if self.m.in_port == other.m.in_port or other.m.in_port == None:
      m.in_port = self.m.in_port 
    else:
      m.in_port = other.m.in_port

    if self.m.dl_src == other.m.dl_src or other.m.dl_src == None:
      m.dl_src = self.m.dl_src 
    else:
      m.dl_src = other.m.dl_src

    if self.m.dl_dst == other.m.dl_dst or other.m.dl_dst == None:
      m.dl_dst = self.m.dl_dst 
    else:
      m.dl_dst = other.m.dl_dst
    
    if self.m.dl_vlan == other.m.dl_vlan or other.m.dl_vlan == None:
      m.dl_vlan = self.m.dl_vlan 
    else:
      m.dl_vlan = other.m.dl_vlan
    
    if self.m.dl_vlan_pcp == other.m.dl_vlan_pcp or other.m.dl_vlan_pcp == None:
      m.dl_vlan_pcp = self.m.dl_vlan_pcp 
    else:
      m.dl_vlan_pcp = other.m.dl_vlan_pcp
    
    if self.m.dl_type == other.m.dl_type or other.m.dl_type == None:
      m.dl_type = self.m.dl_type 
    else:
      m.dl_type = other.m.dl_type
    
    if self.m.nw_tos == other.m.nw_tos or other.m.nw_tos == None:
      m.nw_tos = self.m.nw_tos 
    else:
      m.nw_tos = other.m.nw_tos

    if self.m.nw_proto == other.m.nw_proto or other.m.nw_proto == None:
      m.nw_proto = self.m.nw_proto 
    else:
      m.nw_proto = other.m.nw_proto

    if self.m.nw_src == other.m.nw_src or other.m.nw_src == None:
      m.nw_src = self.m.nw_src 
    else:
      m.nw_src = other.m.nw_src

    if self.m.nw_dst == other.m.nw_dst or other.m.nw_dst == None:
      m.nw_dst = self.m.nw_dst 
    else:
      m.nw_dst = other.m.nw_dst

    if self.m.tp_src == other.m.tp_src or other.m.tp_src == None:
      m.tp_src = self.m.tp_src 
    else:
      m.tp_src = other.m.tp_src

    if self.m.tp_dst == other.m.tp_dst or other.m.tp_dst == None:
      m.tp_dst = self.m.tp_dst 
    else:
      m.tp_dst = other.m.tp_dst

    return Match(m)
