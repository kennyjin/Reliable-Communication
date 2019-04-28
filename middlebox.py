#!/usr/bin/env python3

from switchyard.lib.address import *
from switchyard.lib.packet import *
from switchyard.lib.userlib import *
from threading import *
import random
import time

def drop(percent):
    return random.randrange(100) < percent

def switchy_main(net):

    my_intf = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_intf]
    myips = [intf.ipaddr for intf in my_intf]

    # Read from middlebox_params.txt
    param = open("middlebox_params.txt", "r")
    line = param.readline()
    words = line.split()

    # Extract random seed from params file
    random_seed = (int)(words[1])
    probability_of_drop = (int)(words[3])

    #print(random_seed)
    #print(probability_of_drop)

    # Set random seed
    random.seed(random_seed) 

    while True:
        gotpkt = True
        try:
            timestamp,dev,pkt = net.recv_packet()
            log_debug("Device is {}".format(dev))
        except NoPackets:
            log_debug("No packets available in recv_packet")
            gotpkt = False
        except Shutdown:
            log_debug("Got shutdown signal")
            break

        if not gotpkt:
            continue

        if gotpkt:
            log_debug("I got a packet {}".format(pkt))

        if dev == "middlebox-eth0":
            log_debug("Received from blaster")

            # Get sequence number of ack
            seqnum_byte = (pkt[3].data)[0 : 4]
            seqnum = (struct.unpack(">I", seqnum_byte))[0]

            print("Received Pkt: " +  str(seqnum))

            '''
            Received data packet
            Should I drop it?

            If not, modify headers & send to blastee
            '''
            # Randomly drop packets

            num = random.randint(1, 100)
            if num <= probability_of_drop:
                log_debug("Dropped a packet {}".format(pkt))
                print(num)
                #print("Dropped a packet {}".format(pkt))
                continue

            # Modify Ethernet header
            # Send from eth1 to blastee
            # TODO I assume strings will be directly converted to MAC addr.
            pkt[Ethernet].src = '40:00:00:00:00:02' 
            pkt[Ethernet].dst = '20:00:00:00:00:01'

            net.send_packet("middlebox-eth1", pkt)
        elif dev == "middlebox-eth1":
            log_debug("Received from blastee")

            # Get sequence number of ack
            ack_seqnum_byte = (pkt[3].data)[0 : 4]
            ack_seqnum = (struct.unpack(">I", ack_seqnum_byte))[0]

            print("Received Ack Pkt: " +  str(ack_seqnum))

            '''
            Received ACK
            Modify headers & send to blaster. Not dropping ACK packets!
            '''
            # Modify Ethernet header
            # Send from eth0 to blaster
            # TODO I assume strings will be directly converted to MAC addr.
            pkt[Ethernet].src = '40:00:00:00:00:01'
            pkt[Ethernet].dst = '10:00:00:00:00:01'
            net.send_packet("middlebox-eth0", pkt)
            
        else:
            log_debug("Oops :))")

    net.shutdown()
