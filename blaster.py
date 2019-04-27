#!/usr/bin/env python3

from switchyard.lib.address import *
from switchyard.lib.packet import *
from switchyard.lib.userlib import *
from random import randint
import time
import struct

def print_output(total_time, num_ret, num_tos, throughput, goodput):
    print("Total TX time (s): " + str(total_time))
    print("Number of reTX: " + str(num_ret))
    print("Number of coarse TOs: " + str(num_tos))
    print("Throughput (Bps): " + str(throughput))
    print("Goodput (Bps): " + str(goodput))

    
def switchy_main(net):
    my_intf = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_intf]
    myips = [intf.ipaddr for intf in my_intf]

    # TODO These are for debugging purpose, delete afterwards
    num_pkts = 10 
    num_recvd = 0

    while True:
        # TODO These are for debugging purpose, delete afterwards
        if num_recvd == num_pkts:
            break


        gotpkt = True
        # The sequence number of a packet
        seqnum = 0
        try:
            #Timeout value will be parameterized!
            timestamp,dev,pkt = net.recv_packet(timeout=0.15)
        except NoPackets:
            log_debug("No packets available in recv_packet")
            gotpkt = False
        except Shutdown:
            log_debug("Got shutdown signal")
            #print_output(0,0,0,0,0)
            break

        if gotpkt:

            # TODO This is for debugging purpose, delete afterwards
            num_recvd += 1 
            log_debug("I got a packet")
            
        else:
            log_debug("Didn't receive anything")

            '''
            Creating the headers for the packet
            '''
            pkt = Ethernet() + IPv4() + UDP()
            pkt[0].src = "10:00:00:00:00:01"
            pkt[0].dst = "40:00:00:00:00:01"
            pkt[0].ethertype = EtherType.IPv4
            pkt[1].protocol = IPProtocol.UDP
            # TODO Not very sure about this
            pkt[1].src = "192.168.100.1"
            pkt[1].dst = "192.168.200.1"
            # Set arbituary values for UDP headers
            pkt[2].src = 4444
            pkt[2].dst = 5555
            seqnum += 1
            # Make the sequence number into a byte object with a length of 4 bytes (32 bits)
            # Used big-endian encoding
            seqnum_byte = struct.pack(">I", seqnum)
            payload_byte = b"These are some application data bytes"
            payload_length = len(payload_byte)
            # Make the payload length into a byte object with a length of 2 bytes (16 bits)
            # Used big-endian encoding
            payload_length_byte = struct.pack(">H", payload_length)
            pkt += seqnum_byte
            pkt += payload_length_byte
            pkt += payload_byte
            log_debug("Pkt: {}".format(pkt))
            '''
            Do other things here and send packet
            '''
            net.send_packet("blaster-eth0", pkt)

    net.shutdown()
