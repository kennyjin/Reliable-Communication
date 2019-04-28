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
            # Only acknowledge IPv4 packets
            if pkt[Ethernet].ethertype != EtherType.IPv4:
                continue
            if not pkt.has_header(IPv4):
                continue
            if not pkt.has_header(UDP):
                continue

            # Extract the sequence number info from the received data packet. 
            # Create an ACK packet with the same sequence number.
            ack = Ethernet() + IPv4() + UDP()
            ack[0].src = pkt[0].dst
            ack[0].dst = pkt[0].src
            ack[0].ethertype = EtherType.IPv4
            ack[1].protocol = IPProtocol.UDP
            # TODO Not very sure about this
            ack[1].src = pkt[1].dst
            ack[1].dst = pkt[1].src
            # Set values for UDP headers
            ack[2].src = pkt[2].dst
            ack[2].dst = pkt[2].src

            # Set sequence number bytes for ack
            # Get bit 0 to bit 32
            seqnum_byte = (pkt[3].data)[0 : 4]
            ack += seqnum_byte

            # DEBUG
            seqnum = (struct.unpack(">I", seqnum_byte))[0]

            print("Received Pkt: " +  str(seqnum))

            # Try converting RawPacketContents into bytes
            # Get bit 48 to the end
            payload_byte = (pkt[3].data)[6 : ]

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
