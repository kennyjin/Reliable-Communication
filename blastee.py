#!/usr/bin/env python3

from switchyard.lib.address import *
from switchyard.lib.packet import *
from switchyard.lib.userlib import *
from threading import *
import time

def switchy_main(net):
    my_interfaces = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_interfaces]

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

        if gotpkt:
            log_debug("I got a packet from {}".format(dev))
            log_debug("Pkt: {}".format(pkt))
            # Extract the sequence number info from the received data packet. 
            # Create an ACK packet with the same sequence number.
            ack = Ethernet() + IPv4() + UDP()
            ack[0].src = pkt[0].dst
            ack[0].dst = pkt[0].src
            ack[0].ethertype = EtherType.IPv4
            ack[1].protocol = IPProtocol.UDP
            # TODO Not very sure about this
            ack[1].src = pkt[0].dst
            ack[1].dst = pkt[0].src
            # Set values for UDP headers
            ack[2].src = pkt[2].dst
            ack[2].dst = pkt[2].src

            # Set sequence number bytes for ack
            seqnum_byte = pkt[3]
            ack += seqnum_byte

            # Try converting RawPacketContents into bytes
            payload_byte = (bytes)pkt[5]

            payload_length = len(payload_byte)

            # When the length is smaller than 8, add padding
            if payload_length < 8:
            	payload_byte += "\0".encode() * (8 - payload_length)

            # Get the first 8 bytes
            payload_byte = payload_byte[0:8]

            ack += payload_byte

            log_debug("Ack Pkt: {}".format(ack))

            net.send_packet("blastee-eth0", ack)




    net.shutdown()
