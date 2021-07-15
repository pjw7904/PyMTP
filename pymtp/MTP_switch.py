'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 07/15/2021
Desc: The driver/main logic for a Data Center Network based Meshed Tree Protocol (DCN-MTP)
      implementation. This results in a basic, python-based software switch that utilies DCN-MTP.
'''
from MTPSendRecv import * # Transmit, receive, build, and parse MTP messages
from NetUtils import * # Local network configuration information
from socket import socket, AF_PACKET, SOCK_RAW, ntohs # Build raw sockets
from PIDTable import PIDTable # Insert and access DCN-MTP forwarding table
import argparse # Command-line input


def parseArgs():
    # Read in command-line arguments for start-up switch configuration, if necessary
    argParser = argparse.ArgumentParser(description = "DCN-MTP Software Switch")
    argParser.add_argument('--leaf') # ARG: starting VID
    args = argParser.parse_args()

    return args # return the results of the given CLI input


def main():
    # Read in command-line arguments to determine if node is a leaf or spine node
    args = parseArgs()

    # Create a raw socket where frames can be received, only MTP Ethertype frames for now
    s = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_TYPE_MTP))

    # If the node is leaf switch
    if(args.leaf):
        leafProcess(args.leaf, s)
    else:
        spineProcess(s)

    return


def leafProcess(leafID, recvSoc):
    # Create a DCN-MTP forwarding table for a LEAF node
    leafTable = PIDTable()
    return


def spineProcess(recvSoc):
    # Create a DCN-MTP forwarding table for a SPINE node
    spineTable = PIDTable()
    return


# Switch code starts here, calls main function
if __name__ == "__main__":
    main() # run main