from match import *

class PacketSet(object):
  """
  A PacketSet specifies a set of packets, via an OpenFlow-like
  match on the header fields, and the DPID of the switch at
  which the packet is located.
  """

  def __init__(self, match, dpid):
    """
    match : Match
    dpid : int
    """
    assert isinstance(match, Match)
    assert type(dpid) == int
    self.match = match
    self.dpid = dpid

  def __str__(self):
    return "PacketSet(" + self.match.__str__() + ", " + str(self.dpid) + ")"

  def __repr__(self):
    return "PacketSet(" + self.match.__repr__() + ", " + str(self.dpid) + ")"

  def get_match(self):
    """
    Returns this PacketSet's ofp_match.
    """
    return self.match.m

  def get_dpid(self):
    """
    Returns this PacketSet's DPID.
    """
    return self.dpid

  def eq(self, other):
    """
    Returns True iff this PacketSet equals other (i.e., they represent
    the same set of packets).

    other : PacketSet
    """
    assert isinstance(other, PacketSet)
    return self.dpid == other.dpid \
      and self.match.eq(other.match)

  def subset(self, other):
    """
    Returns True iff the set of packets represented by this PacketSet
    is a subset of the set of packets represented by other.

    other : PacketSet
    """
    assert isinstance(other, PacketSet)
    return self.dpid == other.dpid \
      and self.match.subset(other.match)

  def overlap(self, other):
    """
    Returns True iff the set of packets represented by this PacketSet
    has a non-empty intersection with the set of packets represented by other.

    other : PacketSet
    """
    assert isinstance(other, PacketSet)
    return self.dpid == other.dpid \
      and self.match.overlap(other.match)

  def intersect(self, other):
    """
    Returns a new PacketSet which represented all of the packets which
    both this PacketSet and other represent.

    If this PacketSet and other don't overlap, then returns None.

    other : PacketSet
    """
    if not self.overlap(other):
      return None
    return PacketSet(self.match.intersect(other.match), self.dpid)
