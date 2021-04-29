'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 04/28/2021
Desc: A basic script to test receiving an MTP frame. Use in conjunction with "mtpSendTest.py" for basic testing.
'''

from scapy.all import * # import all of the default scapy library
from mtp import MTP, MTP_Path # import MTP headers
import sys # for command-line input


def main():
    # Decide how you want to output the recieved frames [console/pcap]
    output = sys.argv[1]
    
    # Get the interface to receive the frame from via a command-line argument
    inIntf = sys.argv[2]

    # Record incoming frames and display their content
    if output == "console":
        sniff(iface=inIntf, prn=lambda x: x.show())
    elif output == "pcap":
        mtpPcap = sniff(iface=inIntf)
        wrpcap('MtpTestFrames.pcap', mtpPcap)
    else:
        print("please enter \"console\" for console/text output and \"pcap\" for a pcap file as output")


if __name__ == "__main__":
    main() # run main