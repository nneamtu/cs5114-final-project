#!/usr/bin/env python

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.log import setLogLevel

class HW2Topo(Topo):
  def __init__(self, **opts):
    Topo.__init__(self, **opts)
    h1 = self.addHost('h1')
    h2 = self.addHost('h2')
    h3 = self.addHost('h3')
    h4 = self.addHost('h4')
    h5 = self.addHost('h5')
    h6 = self.addHost('h6')
    s1 = self.addSwitch('s1')
    s2 = self.addSwitch('s2')
    s3 = self.addSwitch('s3')
    s4 = self.addSwitch('s4')
    s5 = self.addSwitch('s5')
    s6 = self.addSwitch('s6')

    self.addLink(h1, s1, bw=100)
    self.addLink(s1, s2, bw=100)
    self.addLink(s1, s3, bw=100)
    self.addLink(s1, s4, bw=100)
    self.addLink(s1, s5, bw=100)
    self.addLink(s1, s6, bw=100)
    
    self.addLink(h2, s2, bw=100)
    self.addLink(s2, s3, bw=100)
    self.addLink(s2, s4, bw=100)
    self.addLink(s2, s5, bw=100)
    self.addLink(s2, s6, bw=100)

    self.addLink(h3, s3, bw=100)
    self.addLink(s3, s4, bw=100)
    self.addLink(s3, s5, bw=100)
    self.addLink(s3, s6, bw=100)

    self.addLink(h4, s4, bw=100)
    self.addLink(s4, s5, bw=100)
    self.addLink(s4, s6, bw=100)

    self.addLink(h5, s5, bw=100)
    self.addLink(s5, s6, bw=100)

    self.addLink(h6, s6, bw=100)
         
if __name__ == '__main__':
  setLogLevel( 'info' )
  topo = HW2Topo()
  net = Mininet(topo=topo, link=TCLink, autoSetMacs=True, autoStaticArp=True,
          controller=RemoteController(name="manager", port=6633))
  net.start()
  CLI( net )
  net.stop()