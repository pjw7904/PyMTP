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
import netifaces as ni


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

    # If the node is a leaf switch
    if(args.leaf):
        leafProcess(args.leaf, s)
    else: # If the node is a spine switch
        spineProcess(s)

    return


def leafProcess(hostInt, recvSoc):
    # Create a DCN-MTP forwarding table for a LEAF node
    leafTable = PIDTable()

    # Get the valid interface names on the node
    intList = getLocalInterfaces()
    intList.remove(hostInt) # We don't want to look at this right now, just spine ints
    print("spine ints: ", intList)

    # Determine LeafID from the host interface
    leafID = ni.ifaddresses(hostInt)[ni.AF_INET][0]['addr'].split(".")[2]
    print("leaf ID", leafID)

    # Send Leaf Annoucement messages to each spine
    for int in intList:
        ancmtMsg = buildAnnouncementMsg(leafID, int)
        sendMTPMsg(ancmtMsg, int)

    # Get aquainted with every spine node before continuing on
    while(intList):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        if(MTPMessageType == MTP_ANNOUNCEMENT):
            PID = "{0}.{1}".format(receivedFrame[MTP].leafID.decode(), receivedFrame[MTP].spineID.decode())
            leafTable.addChild(PID, receivedPort)
            leafTable.getTables()
        else:
            print("ERROR: unknown message type")

    return


def spineProcess(recvSoc):
    # Create a DCN-MTP forwarding table for a SPINE node
    spineTable = PIDTable()

    # Pre-build a join message to send to neighbors
    joinMsg = buildJoinMsg()


    # Loop through the switching logic until the switch is shut down
    switchIsActive = True
    while(switchIsActive):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        if(MTPMessageType == MTP_ANNOUNCEMENT):
            receivedFrame.show2()
            PID = "{0}.{1}".format(receivedFrame[MTP].leafID.decode(), receivedFrame[MTP].spineID.decode())
            spineTable.addParent(PID, 1, receivedPort) # Cost of one (second argument)
            spineTable.getTables()

    return


# Switch code starts here, calls main function
if __name__ == "__main__":
    main() # run main