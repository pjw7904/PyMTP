'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 04/28/2021
Desc: A basic script to test building and sending a frame which includes an MTP header with path information (MTP advertisement).
      The associated "mtpRecvTest.py" can be used as a target for this frame to make sure it transfer over a network correctly.
'''
from scapy.all import * # import all of the default scapy library
from mtp import MTP, MTP_Path # import MTP headers
import sys # for command-line input


def main():
    # Get the interface to send the frame out of via a command-line argument
    outIntf = sys.argv[1]

    # Get the destination (Eth II) via a command-line argument
    destMAC = sys.argv[2] 

    #Build a fake/test path bundle, which, when sent over the network, will be comprised of a collection of MTP_Path headers each describing a single path in the bundle
    path1 = MTP_Path(cost=2, path="1.2.3")
    path2 = MTP_Path(cost=3, path="1.1.2.3")
    path3 = MTP_Path(cost=4, path="1.2.4.3")

    # Group the individual path headers into a list
    pathBundlePathHeaders = [path1, path2, path3]

    # Build the MTP header, which will be a path bundle advertisement message encapsulated in an Ethernet II header with ethertype 0x4133. Note that the paths are added as sub-headers to the normal MTP header.
    MTPFrame = Ether(dst=destMAC, type=0x4133)/MTP(type=3, operation=1, port=5, paths=pathBundlePathHeaders)

    # Send the frame
    sendp(MTPFrame, iface=outIntf, count=1, verbose=False)

    print("MTP frame sent!")


if __name__ == "__main__":
    main() # run main