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
