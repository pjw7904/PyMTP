'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 07/15/2021
Desc: Defines how to build, parse, transmit, and receive frames which include MTP headers.
'''
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import sendp # import necessary headers and functions
from mtp import MTP, MTP_Path # import MTP headers

# Set constants for communication
DEST_MTP_PHY_ADDR = "01:80:c2:00:00:ff" # Reserved IEEE non-forwarded multicast address
RECV_BUF_SIZE = 4096 # Take in 4096 bytes for each socket recv call
ETH_TYPE_MTP = 0x4133 # Ethertype for MTP-in-Ethernet encapsulation

# MTP message types
MTP_ANNOUNCEMENT = 1
MTP_ROUTED = 9


def buildAnnouncementMsg(leafID, outInt):
    intNumber = int(outInt.strip("eth")) # Get the int number only, no "eth" in front
    ancmtMsg = Ether(dst=DEST_MTP_PHY_ADDR, type=ETH_TYPE_MTP)/MTP(type=MTP_ANNOUNCEMENT, leafID=leafID, spineID=intNumber)

    return ancmtMsg


# Sending an MTP message out of a given interface
def sendMTPMsg(MT_PKT, outInt):
    # Send the frame
    sendp(MT_PKT, iface=outInt, count=1, verbose=False)

    return