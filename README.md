# Note

I left the code for the examples out of this public repo, since they contain 
partial solutions to homework assignments.

# Building

This project uses Mininet and POX.  I ran my code using the Mininet VM.

# Demo

There are 5 examples that you can run (examples A-E as explained in the report).

You must configure the manager with which example you want to run. 
To do that, modify line 34 in `manager.py`.

To start the controller, run:

`/home/mininet/pox/pox.py manager`

You must also run Mininet with the correct topology for the example (as noted below).
The topology files are called `topo_a.py` and `topo_b.py`.
Topology A is the topology from the IP load balancer on Homework 1, and
Topology B is the topology from Homework 2.

To start Mininet, run:

`sudo python topo_X.py`

To get an overview of the modules used in each example, you may either 
reference the report, or the documentation inside each module 
(e.g. `example_a/firewall.py`).

## Example A

Uses Topology A. Firewall and proactive routing sub-controllers.

Both of these modules are proactive, so after starting Mininet,
you can inspect the flows on `s1` to see the rules that are installed.

## Example B

Uses Topology A. Firewall, load balancer, reactive routing sub-controllers.

This example works like the IP load balancer from Homework 1. So, you should
run `h1 arp -s 10.0.0.99 99:99:99:99:99:99` once you start Mininet.
Note that this example only routes TCP/UDP flows.

To test the load balancer, you can do `h1 wget http://10.0.0.99:8000/`.
The controller will print out "Rule added by 1 : ...", since the
load balancer has index 1 in the ordered list of sub-controllers.

To test the routing sub-controller, you can do `h2 wget http://10.0.0.3:8000/`.
The controller will now print out "Rule added by 2 : ...", since the
routing sub-controller has index 2.

You can also inspect the flows on `s1` to see each rule installed at the
normal priority for the corresponding sub-controller.

## Example C

Uses Topology B. VLB and proactive routing sub-controllers.

Before doing anything, you can see the reservation rule installed with priority
3 at each of the switches `s1-s6`.

Now, to create a TCP flow, you can do `h1 wget http://10.0.0.2:8000/`.
This causes the VLB sub-controller to add some rules, and you can see that
they are installed with priority 4.

To test the routing sub-controller, we need to do something that doesn't use
TCP, such as ping: `h1 ping h2 -c 5`. You can observe that no new rules
are added, and the normal rules with priority 1 are used to forward these packets.

## Example D

Uses Topology B. VLB (without SSH) and proactive routing sub-controllers.

Before doing anything, you can see the shared rules installed with priority 6
on each of the switches `s1-s6`.

Aside from this, this example behaves the same as Example C.

## Example E

Uses Topology B. Even-host-observer and proactive routing sub-controllers.

Before doing anything, you can see the shared rules installed in `s2`, `s4`, 
and `s6`.

You can test the even-host-observer by doing e.g., `h1 ping h2 -c 5`.
For each packet from `h2` that is "observed", the controller will print
out "Packet observed from switch..."
