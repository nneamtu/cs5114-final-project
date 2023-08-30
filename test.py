from packet_set import PacketSet
from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from match import *
from packet_set import *
from shared import *

m1 = Match(of.ofp_match(in_port = 1, nw_src = "10.0.0.1"))
m2 = Match(of.ofp_match(in_port = 1))
m3 = Match(of.ofp_match(in_port = 1, nw_src = "10.0.0.1"))
m4 = Match(of.ofp_match(in_port = 2, nw_src = "10.0.0.1"))
m5 = Match(of.ofp_match(in_port = 1, nw_dst = "10.0.0.2"))
m6 = Match(of.ofp_match(in_port = 1, nw_src = "10.0.0.1", nw_dst = "10.0.0.2"))

def match_tests():
  # equality tests
  assert m1.eq(m3)
  assert not m1.eq(m2)
  assert not m1.eq(m5)

  # subset tests
  assert m1.subset(m3)
  assert m1.subset(m2)
  assert m5.subset(m2)
  assert m6.subset(m5)
  assert not m1.subset(m5)
  assert not m1.subset(m4)

  # overlap tests
  assert m1.overlap(m3)
  assert m1.overlap(m2)
  assert m2.overlap(m1)
  assert m1.overlap(m5)
  assert m6.overlap(m1)
  assert not m1.overlap(m4)

  # intersect tests
  assert m1.intersect(m3).eq(m1)
  assert m1.intersect(m2).eq(m1)
  assert m2.intersect(m1).eq(m1)
  assert m1.intersect(m4) == None
  assert m1.intersect(m5).eq(m6)

  print("match tests successful")

ps1 = PacketSet(m1, 1)
ps2 = PacketSet(m2, 1)
ps3 = PacketSet(m3, 1)
ps4 = PacketSet(m4, 1)
ps5 = PacketSet(m5, 1)
ps6 = PacketSet(m6, 1)
ps7 = PacketSet(m1, 2)

def packet_set_tests():
  # equality tests
  assert ps1.eq(ps3)
  assert not ps1.eq(ps2)
  assert not ps1.eq(ps5)
  assert not ps1.eq(ps7)

  # subset tests
  assert ps1.subset(ps3)
  assert ps1.subset(ps2)
  assert ps5.subset(ps2)
  assert ps6.subset(ps5)
  assert not ps1.subset(ps5)
  assert not ps1.subset(ps4)
  assert not ps1.subset(ps7)

  # overlap tests
  assert ps1.overlap(ps3)
  assert ps1.overlap(ps2)
  assert ps2.overlap(ps1)
  assert ps1.overlap(ps5)
  assert ps6.overlap(ps1)
  assert not ps1.overlap(ps4)
  assert not ps1.overlap(ps7)

  # intersect tests
  assert ps1.intersect(ps3).eq(ps1)
  assert ps1.intersect(ps2).eq(ps1)
  assert ps2.intersect(ps1).eq(ps1)
  assert ps1.intersect(ps4) == None
  assert ps1.intersect(ps5).eq(ps6)
  assert ps1.intersect(ps7) == None

  print("packet set tests successful")

pr1 = Priority([1])
pr2 = Priority([1])
pr3 = Priority([2])
pr4 = Priority([])
pr5 = Priority([3, 2])
pr6 = Priority([3, 1])
pr7 = Priority([3])
pr8 = Priority([2, 1])

def priority_tests():
  # eq tests
  assert pr1.eq(pr2)
  assert not pr4.eq(pr1)
  assert not pr1.eq(pr4)
  assert not pr1.eq(pr3)

  # lt tests
  assert not pr4.lt(pr4)
  assert pr4.lt(pr1)
  assert not pr1.lt(pr4)
  assert pr1.lt(pr3)
  assert not pr3.lt(pr1)
  assert pr6.lt(pr5)
  assert not pr5.lt(pr6)
  assert pr7.lt(pr5)
  assert not pr5.lt(pr7)

  # is_empty tests
  assert pr4.is_empty()
  assert not pr1.is_empty()

  # append tests
  assert pr4.append(1).eq(pr1)
  assert pr3.append(1).eq(pr8)

  # extend tests
  assert pr1.extend(pr4).eq(pr1)
  assert pr4.extend(pr1).eq(pr1)
  assert pr3.extend(pr1).eq(pr8)

  # pop tests
  assert pr1.pop().eq(pr4)
  assert pr4.pop().eq(pr4)
  assert pr8.pop().eq(pr1)

  print("priority tests successful")

rules1 = [(ps1, ["a1"], Priority([3]), True), (ps4, ["a2"], Priority([3]), True), (ps5, ["a3"], Priority([3]), True)]
rules2 = [(ps2, ["a4"], Priority([2]), True), (ps4, ["a5"], Priority([2]), False), (ps7, ["a6"], Priority([2]), True)]
rules3 = [(ps1, ["a7"], Priority([1]), True), (ps4, ["a8"], Priority([1]), True)]
rules4 = [(ps1, ["a9"], Priority([0]), True)]

result1 = [(ps1, ["a1", "a4"], Priority([3, 2]), True), (ps5, ["a3", "a4"], Priority([3, 2]), True), (ps4, ["a2", "a5"], Priority([3, 2]), False)] + rules1
result2 = [(ps1, ["a4", "a9"], Priority([2, 0]), True), (ps2, ["a4"], Priority([2]), True), (ps4, ["a5"], Priority([2]), False), (ps7, ["a6"], Priority([2]), True)]
result3 = [(ps1, ["a1", "a4", "a7"], Priority([3, 2, 1]), True), (ps6, ["a3", "a4", "a7"], Priority([3, 2, 1]), True), (ps5, ["a3", "a4"], Priority([3, 2]), True), (ps4, ["a2", "a5"], Priority([3, 2]), False)] + [(ps1, ["a1", "a7"], Priority([3, 1]), True), (ps4, ["a2", "a8"], Priority([3, 1]), True), (ps6, ["a3", "a7"], Priority([3, 1]), True)]+ [(ps1, ["a1", "a4"], Priority([3, 2]), True), (ps5, ["a3", "a4"], Priority([3, 2]), True)] + rules1

num2 = [(ps1, ["a4", "a9"], 10), (ps2, ["a4"], 0), (ps4, ["a5"], 0), (ps7, ["a6"], 0)]
num3 = [(ps1, ["a1", "a4", "a7"], 10), (ps6, ["a3", "a4", "a7"], 10), (ps5, ["a3", "a4"], 0), (ps4, ["a2", "a5"], 0)]

def shared_eq(p1, p2):
  (ps1, a1, pr1, b1) = p1
  (ps2, a2, pr2, b2) = p2
  return ps1.eq(ps2) and pr1.eq(pr2) and b1 == b2

def shared_list_mem(p, l):
  for x in l:
    if shared_eq(p, x):
      return True
  return False

def shared_list_eq(l1, l2):
  for x in l1:
    if not shared_list_mem(x, l2):
      return False
  for y in l2:
    if not shared_list_mem(y, l1):
      return False
  return True

def shared_tests():
  # compute_shared_rules_l tests
  shared1 = compute_shared_rules_l(rules1, rules2)
  #print(shared1)
  assert shared_list_eq(shared1, result1)

  shared2 = compute_shared_rules_l(rules2, rules4)
  #print(shared2)
  assert shared_list_eq(shared2, result2)

  shared3 = compute_shared_rules_l(shared1, rules3)
  #print(shared3)
  assert shared_list_eq(shared3, result3)

  numerical2 = [(ps, a, pr.to_num()) for (ps, a, pr, _) in shared2]
  print(numerical2)
  numerical3 = [(ps, a, pr.to_num()) for (ps, a, pr, _) in shared3]
  print(numerical3)

  print("passing tests successful")

match_tests()
packet_set_tests()
priority_tests()
shared_tests()
