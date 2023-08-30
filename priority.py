class Priority(object):
  """
  Symbolic representation of priorities, used for ordering passed rules.

  Priorities are represented as a list. 
    n ::= naturals
    p ::= [] | n :: p
  """

  def __init__(self, p):
    """
    Creates Priority representing given list.
    p : list of non-negative integers
    """
    self.p = p
    assert type(p) == list 
    for n in p:
      assert type(n) == int and n >= 0

  def __str__(self):
    return "Priority(" + str(self.p) + ")"

  def __repr__(self):
    return "Priority(" + str(self.p) + ")"

  def is_empty(self):
    """
    Returns True iff this Priority represents the empty list.
    """
    return self.p == []

  def append(self, n):
    """
    Returns new Priority by appending n to the symbolic priority.
    n : int, non-negative
    """
    assert type(n) == int and n >= 0
    return Priority(self.p + [n])

  def extend(self, other):
    """
    Returns new Priority by extending this priority with that of other.
    other : Priority
    """
    assert isinstance(other, Priority)
    return Priority(self.p + other.p)

  def pop(self):
    """
    Returns new Priority by popping first element off of symbolic priority.
    If this Priority is empty, then returns a new empty Priority.
    """
    if self.p == []:
      return Priority([])
    else:
      return Priority(self.p[1:])

  def eq(self, other):
    """
    Returns True iff this Priority is equal to other.

    Equality between priorities is established element-wise:
          [] = []
      n :: p = n' :: p' if n = n' and p = p'

    other : Priority
    """
    assert isinstance(other, Priority)
    if self.p == [] and other.p == []:
      return True
    elif len(self.p) > 0 and len(other.p) > 0:
      return self.p[0] == other.p[0] and self.pop().eq(other.pop())
    else:
      return False

  def lt(self, other):
    """
    Returns True iff this Priority is (strictly) less than other.

    Priorities are ordered as follows:
          [] < h :: _
      l :: _ < h :: _  if l < h
      h :: p < h :: p' if p < p'

    other : Priority
    """
    assert isinstance(other, Priority)
    if self.p == []:
      return other.p != []
    elif len(self.p) > 0 and len(other.p) > 0:
      if self.p[0] < other.p[0]:
        return True
      elif self.p[0] == other.p[0]:
        return self.pop().lt(other.pop())
    else:
      return False

  def to_num(self):
    """
    Converts this Priority to its numerical representation.

    This is defined as follows:
      to_num([]) = 0
      to_num(p :: n) = to_num(p) + 2 ** n
    """
    sum = 0
    for n in self.p:
      sum += 2 ** n
    return int(sum)