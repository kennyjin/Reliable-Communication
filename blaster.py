#!/usr/bin/env python3

from switchyard.lib.address import *
from switchyard.lib.packet import *
from switchyard.lib.userlib import *
from random import randint
import time
import struct

def make_pkt(seqnum, payload_length):
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
    # seqnum += 1
    # Make the sequence number into a byte object with a length of 4 bytes (32 bits)
    # Used big-endian encoding
    seqnum_byte = struct.pack(">I", seqnum)
    # payload_byte = b"These are some application data bytes"
    # payload_byte = b"bytes"
    # payload_length = len(payload_byte)
    # Generate payload according to the given length
    payload_byte = ("a" * payload_length).encode()
    # Make the payload length into a byte object with a length of 2 bytes (16 bits)
    # Used big-endian encoding
    payload_length_byte = struct.pack(">H", payload_length)
    pkt += seqnum_byte
    pkt += payload_length_byte
    pkt += payload_byte
    return pkt

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

    param = open("blaster_params.txt", "r")
    line = param.readline()
    words = line.split()

    num_pkts = (int)(words[1])
    payload_length = (int)(words[3])
    SW = (int)(words[5])
    coarse_timeout = (float)(words[7]) # milliseconds
    recv_timeout = (float)(words[9]) # milliseconds

    # TODO These are for debugging purpose, delete afterwards
    # num_pkts = 10 
    num_sent = 0
    num_recvd = 0

    # The sequence number of a packet
    seqnum = 0

    # The sender window dictionary of timeouts
    # Maps sequence number to time
    SW_dict_time = {}

    # The sender window dictionary of acks
    # Maps sequence number to the state of ack (True or False)
    SW_dict_acked = {}

    # The 2 variables used in sender window
    LHS = RHS = 1

    while True:

        print("LHS = " + LHS)
        print("RHS = " + RHS)
        # TODO These are for debugging purpose, delete afterwards
        if num_recvd == num_pkts:
            print(SW_dict_time)
            print(SW_dict_acked)
            break


        gotpkt = True
        
        try:
            #Timeout value will be parameterized!
            timestamp,dev,pkt = net.recv_packet(timeout = recv_timeout / 1000)
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

            log_debug("Pkt: {}".format(pkt))

            print("Received Pkt: {}".format(pkt))

            # Get sequence number of ack
            ack_seqnum_byte = (pkt[3].data)[0 : 4]
            ack_seqnum = (struct.unpack(">I", ack_seqnum_byte))[0]

            # May add sanity check, i.e, check if the seqnum exist in dict

            # Mark as acked
            SW_dict_acked[ack_seqnum] = True

            # Check if seqnum == LHS
            # If so, move LHS to the right until see an unacked pkt
            if ack_seqnum == LHS:
                for i in range(LHS, RHS):
                    if SW_dict_acked[i] == True:
                        LHS = i + 1
                    else :
                        break






        else:
            log_debug("Didn't receive anything")

            # set flag to record if a pkt has been sent
            flag = False

            # Check for timeout and unacked packet
            for i in range(LHS, RHS):
                if (SW_dict_acked[i] == False) and (SW_dict_time[i] - time.time() > coarse_timeout / 1000):
                    # TODO make packet
                    pkt = make_pkt(i, payload_length)
                    # send packet
                    net.send_packet("blaster-eth0", pkt)
                    # reset timer
                    SW_dict_time[i] = time.time()
                    flag = True

                    print("Resent Pkt: {}".format(pkt))
                    # break the for loop
                    break

            # continue for while loop
            if flag == True:
                continue

            # TODO This is for debugging purpose, delete afterwards
            if num_sent == num_pkts:
                continue

            if RHS == LHS + SW:
                continue

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

            # payload_byte = b"These are some application data bytes"
            # payload_byte = b"bytes"
            # payload_length = len(payload_byte)

            # Generate payload according to the given length
            payload_byte = ("a" * payload_length).encode()

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
            SW_dict_time[seqnum] = time.time()
            SW_dict_acked[seqnum] = False

            RHS += 1

            # TODO This is for debugging purpose, delete afterwards
            num_sent += 1

            print("Sent Pkt: {}".format(pkt))

    net.shutdown()
