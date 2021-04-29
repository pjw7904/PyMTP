'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 04/28/2021
Desc: A basic script to test receiving an MTP frame. Use in conjunction with "mtpSendTest.py" for basic testing.
'''

from scapy.all import * # import all of the default scapy library
from mtp import MTP, MTP_Path # import MTP headers
import sys # for command-line input


def main():

    # Get the interface to receive the frame from via a command-line argument
    inIntf = sys.argv[1]

    # Record incoming frames and display their content
    sniff(iface=inIntf, prn=lambda x: x.show())


if __name__ == "__main__":
    main() # run main