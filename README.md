# Traceroute
A simple command-line tracert implementation in Python using ICMP packets

![Screenshot](https://github.com/James-P-D/Traceroute/blob/master/screenshot.gif)

## Details

Traceroute is a networking tool designed for tracing the movement of packets across a network. In this Python 3 implementation, [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol) 'ping' packets are used, much like the Windows `tracert.exe` program (and unlike Unix `tracert` which typically uses UDP packets).

The application sends a sequence of ICMP packets to the host, initially with the [Time-To-Live](https://en.wikipedia.org/wiki/Time_to_live) field set to `1`. As the packet travels across the network to its final destination, each node it passes through will decrement the TTL field by `1`. When the field reaches zero the node will respond by saying that the packet could not reach its destination. Having now identified the first node that the packet passes through, tracert now sends another ICMP packet with TTL set to `2`, which will timeout when it reaches the second node, and so on.

Eventually, an ICMP packet will be sent with a sufficiently large TTL value that it can reach the final destination, at which point the process is complete.