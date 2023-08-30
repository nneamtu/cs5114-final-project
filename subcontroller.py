class Subcontroller():
  """
  Base class for sub-controllers.

  All sub-controllers must provide this interface.
  """

  def handle_connection_up(self, event):
    """
    Handler for ConnectionUp event.
    """
    pass
  
  def handle_connection_down(self, event):
    """
    Handler for ConnectionDown event.
    """
    pass

  def handle_flow_removed(self, event):
    """
    Handler for FlowRemoved event.
    """
    pass

  def handle_port_status(self, event):
    """
    Handler for PortStatus event.
    """
    pass

  def handle_packet_in(self, event):
    """
    Handler for PacketIn event.
    Returns True if this sub-controller has finished processing the packet,
    False if this packet should be passed to next sub-controller.
    """
    pass

  def handle_reserved_packet(self, event):
    """
    Handler for receipt of packet in reserved flow.
    Returns True if this sub-controller has finished processing the packet,
    False if this packet should be passed to next sub-controller.
    """
    pass