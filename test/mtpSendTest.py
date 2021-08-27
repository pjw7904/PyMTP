'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 08/27/2021
Desc: A basic script to test building and sending a frame which includes an MTP header with path information.
      The associated "mtpRecvTest.py" can be used as a target for this frame to make sure it transfer over a network correctly.
'''
import sys
sys.path.append("../pymtp")

from scapy.all import * # import all of the default scapy library
from mtp import MTP # import MTP headers
import sys # for command-line input


def main():
    # Get the interface to send the frame out of via a command-line argument
    outIntf = sys.argv[1]

    # Get the destination (Eth II) via a command-line argument
    destMAC = sys.argv[2] 

    #Build a fake list of tier IDs (egress ports)
    spineIDs = [5, 1, 7]

    # Build the MTP header, which will be a path bundle advertisement message encapsulated in an Ethernet II header with ethertype 0x4133. Note that the paths are added as sub-headers to the normal MTP header.
    MTPFrame = Ether(dst=destMAC, type=0x4133)/MTP(type=1, leafID=1, spineID=spineIDs)
    MTPFrame.show2()

    # Send the frame
    sendp(MTPFrame, iface=outIntf, count=1, verbose=False)

    print("MTP frame sent!")


if __name__ == "__main__":
    main() # run main