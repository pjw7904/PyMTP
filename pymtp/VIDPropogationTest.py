'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 05/19/2021
Desc: A basic script to test a basic MT_VID propogation system. To be used on Mininet, GENI, 
      or any network of Scapy-installed devices. Currently DOES NOT work for Scapy 2.4.5, use 2.4.4.
'''

from scapy.all import * # import all of the default scapy library
from mtp import MTP, MTP_Path # import MTP headers
import argparse # for command-line input
import socket # To get interface information, not used for actual sockets


def getLocalInterfaces(intToSkip):
    loopbackIntName = 'lo'

    interfaceList = socket.if_nameindex() # List which includes interface in tuples of (int#, intName)
    filteredIntList = [int[1] for int in interfaceList if int[1] != intToSkip and int[1] != loopbackIntName] # Filter out the int# and any ints to skip over
    return filteredIntList


def sendMTPFrame(MT_PDU, outInt):
    # Send the frame
    sendp(MT_PDU, iface=outInt, count=1, verbose=False)
    
    return


def respondToMTPFrame(MT_PDU):
    
    return "test"


def main():
    broadcastAddr = "ff:ff:ff:ff:ff:ff"

    # Read in command-line arguments for start-up Meshed Tree Switch configuration, if necessary
    argParser = argparse.ArgumentParser(description = "MTP Implementation Simulator")
    argParser.add_argument('--root') # For the root of a meshed tree, which should include the root VID
    argParser.add_argument('--cntrlPort') # If there is an interface that shouldn't be sniffed on (eth0 on GENI, for example)
    args = argParser.parse_args()

    rootVID = args.root # Boolean to check if this node is the root
    intToSkip = args.cntrlPort

    # Start VID propogation process if the node is a root node
    intList = getLocalInterfaces(intToSkip)

    if(rootVID):
        initVID = MTP_Path(cost=1, path=rootVID)

        for interface in intList:
            intNumber = int(interface.strip("eth"))
            MTPFrame = Ether(dst=broadcastAddr, type=0x4133)/MTP(type=3, operation=1, port=intNumber, paths=[initVID])
            sendMTPFrame(MTPFrame, interface)
            print("sent MT_PDU out of interface {0}, which is port number {1}".format(interface, intNumber))

    else:
        # NOTE: Scapy ver. 2.4.5 has a bug which does not allow for multi-int sniffing, use 2.4.4
        sniff(iface=intList, prn=lambda x: x.show())


if __name__ == "__main__":
    main() # run main