from packet_set import *
from priority import *

def compute_shared_rules_l(shared, rules_l):
  """
  Returns set of new shared rules, arising from the given shared rules and
  rules for a single sub-controller (note that any of these rules may or may not
  be sharable).

  Each rule is represented as a 4-tuple:
  - PacketSet
  - action list
  - Priority
  - bool, representing whether it is sharable

  shared : (PacketSet * ofp_action list * Priority * bool) list
  rules_l : (PacketSet * ofp_action list * Priority * bool) list
  """
  new_shared = []
  for (ps1, a1, pr1, sharable1) in shared:
    if sharable1:

      for (ps2, a2, pr2, sharable2) in rules_l:
        if ps1.eq(ps2) or ps1.subset(ps2):
          ps_int = ps1.intersect(ps2)
          new_shared.append((ps_int, a1 + a2, pr1.extend(pr2), sharable2))
        elif ps1.overlap(ps2):
          ps_int = ps1.intersect(ps2)
          new_shared.append((ps_int, a1 + a2, pr1.extend(pr2), sharable2))

  return new_shared

def compute_shared_rules(c_id, c_sharable, c_normal):
  """
  Computes all shared rules for sub-controller with given id that arise
  from the given sharable and normal rules.
  c_sharable has all of the sharable rules for each sub-controller, and is
  indexed by sub-controller id.
  Similarly, c_normal has all of the normal rules for each sub-controller, 
  and is indexed by sub-controller.

  c_id : int
  c_sharable : (PacketSet * ofp_action list) list
  c_normal : (PacketSet * ofp_action list) list
  """
  shared = [(ps, a, Priority([len(c_normal) - c_id - 1]), True) for (ps, a) in c_sharable[c_id]]

  for i in range(c_id + 1, len(c_normal)):
    normal_l = [(ps, a, Priority([len(c_normal) - i - 1]), False) for (ps, a) in c_normal[i]]
    passable_l = [(ps, a, Priority([len(c_normal) - i - 1]), True) for (ps, a) in c_sharable[i]]
    shared.extend(compute_shared_rules_l(shared, normal_l + passable_l))

  return [(ps, a, pr.pop().to_num()) for (ps, a, pr, b) in shared if (not b) or a != []]

def compute_shared_rules_from_id(h_id, l_id, c_sharable, c_normal):
  """
  Computes all shared rules for sub-controller with id h_id which arise from
  the rules for the sub-controller with id l_id. 
  c_sharable has all of the sharable rules for each sub-controller, and is
  indexed by sub-controller id.
  Similarly, c_normal has all of the normal rules for each sub-controller, 
  and is indexed by sub-controller.

  h_id : int
  l_id : int
  c_sharable : (PacketSet * ofp_action list) list
  c_normal : (PacketSet * ofp_action list) list
  """
  shared = [(ps, a, Priority([len(c_normal) - h_id - 1]), True) for (ps, a) in c_sharable[h_id]]
  new_shared = []

  for i in range(h_id + 1, len(c_normal)):
    normal_l = [(ps, a, Priority([len(c_normal) - i - 1]), False) for (ps, a) in c_normal[i]]
    passable_l = [(ps, a, Priority([len(c_normal) - i - 1]), True) for (ps, a) in c_sharable[i]]
    rules = compute_shared_rules_l(shared, normal_l + passable_l)
    shared.extend(rules)
    if l_id <= i:
      new_shared.extend(rules)

  return [(ps, a, pr.pop().to_num()) for (ps, a, pr, b) in new_shared if (not b) or a != []]
