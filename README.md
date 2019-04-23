# Reliable-Communication

## Overview
This is a reliable communication library for Switchyard that consists of 3 agents.

At a high level, a **blaster** will send data packets to a **blastee** through a **middlebox**.

Since IP only offers *best effort service* of delivering packets between hosts, all sort of bad things can happen to packets when they are in the network. they can get *lost*, *arbitrarily delayed* or *duplicated*. This communication libaray provides additional delivery guarantees by implementing some basic mechanisms at **blaster** and **blastee**.

## Details
This reliable commication library implements the following features to provide additional guarantees:

* __ACK mechanism__ on __blastee__ for each successfully received packets.
* A __fixed-size sliding window__ on __blaster__.
* __Timeouts__ on __blaster__ to resend non-ACK'd packets.

## Middlebox

This is a very basic version of the router in P2 (IPv4-Router).
1. The __middlebox__ will have 2 ports with a signle connection: one to the __blaster__ and one to the __blastee__.
2. The same packet header modifications are done as in P2 (__Not sure__).
    * Decrement the TTL field in the IP header by 1.
    * Modify the Ethernet header. There are 3 fields in the Ethernet header. dst, ethertype and src. src is the source mac address.
    ``` python
    src = intf.ethaddr
    ```
    dst is the next hop MAC address.
    Instead of making ARP requests, IP-MAC mappings are hard coded into the middlebox code. This means, if the middlebox receives a packet from its eth0 interface(= from blaster), it will forward it out from eth1(= to blastee) and vice versa. Regardless of the source IP address, just *forward the packet from the other interface.*
3. The middlebox will also be in charge of *probabilistically dropping packets* to simulate all the evil things that can happen in a real network. Packet drops will only happen in *one direction*, from **blaster** to **blastee** (i.e do not drop ACKs)
4. NOTE: the probabilistic drop logic is sketched out the starter file middlebox.py. Use it to keep your drops deterministic.

## Blastee

Blastee will receive data packets from the blaster and immediately ACK them.

1. Extract the sequence number information from the received data packet. 
2. Create an ACK packet with the same sequence number.

## Blaster

Blaster will send/receive variable sized IP packets/ACKs to/from the blastee.  A fixed sized sender window (SW) is implemented at packet granularity.

Two variables are defined to described how SW will work.

* _LHS_: The number corresponding to the smallest numbered unACKed packet of the SW.
* _RHS_: The number corresponding to the next packet to be transmitted.

2 conditions are always needed to be satisfied:

* RHS - LHS <= SW
* Every packet with sequence number Sj < Si has been successfully ACKed. (__Not sure what is the seq number here__) 

Whenever a packet has not been ACKed for a certain amount of time, the blaster will __time out__ and retransmit the packet in the current window that has't been ACKed yet.

## Packet Format


##  Running the code
The implementations will be run in Mininet. A topology file (start_mininet.py) is provided. Do not change the addresses (IP and MAC) or node/link setup. When testing, different delay values might be used.

To spin up the agents in Mininet, open up a terminal and type the following command:

```
$ sudo python start_mininet.py
```

Open up a xterm on each agent:

```
mininet> xterm blaster
mininet> xterm blastee
mininet> xterm middlebox
```

Start the agents:

```
blastee# ./switchyard/swyard.py blastee.py

middlebox# ./switchyard/swyard.py middlebox.py

blaster# ./switchyard/swyard.py blaster.py
```

Note: Run **blaster** file only after you run your **middlebox** and **blastee** file.

Parameters will need to be specified when running the agents. There will be 3 files in the working directory: (**Not sure if there will be blastee_param.txt**)

* blaster_params.txt
* blastee_params.txt
* middlebox_params.txt
