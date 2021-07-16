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

    # If the node is a leaf switch
    if(args.leaf):
        leafProcess(args.leaf, s)
    else:
        spineProcess(s)

    return


def leafProcess(leafID, recvSoc):
    # Create a DCN-MTP forwarding table for a LEAF node
    leafTable = PIDTable()

    # Pre-build the MTP advt path header to send to spines who request it
    leafIDPath = MTP_Path(cost=1, path=leafID)

    '''
    Adding IPv4 subnets on host ports to table
    goes here
    '''

    # Loop through the switching logic until the switch is shut down
    switchIsActive = True
    while(switchIsActive):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        if(MTPMessageType == MTP_HELLO):
            print("Hello message received")
        
        elif(MTPMessageType == MTP_JOIN):
            advtMsg = buildAdvtMsg([leafIDPath], 1, receivedPort)
            sendMTPMsg(advtMsg, receivedPort)
            print("Sent the following message:")
            advtMsg.show2()

        elif(MTPMessageType == MTP_ADVT):
            print("ERROR: Join message received")
        else:
            print("ERROR: unknown message type")


    return


def spineProcess(recvSoc):
    # Create a DCN-MTP forwarding table for a SPINE node
    spineTable = PIDTable()

    # Get the valid interface names on the node
    intList = getLocalInterfaces()

    # Pre-build a join message to send to neighbors
    joinMsg = buildJoinMsg()

    # Ask for Path ID information from all neighbors
    for interface in intList:
        intNumber = int(interface.strip("eth")) # Get the int number only, no "eth" in front
        sendMTPMsg(joinMsg, interface)

    # Loop through the switching logic until the switch is shut down
    switchIsActive = True
    while(switchIsActive):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        if(MTPMessageType == MTP_ADVT):
            receivedFrame.show2()

    return


# Switch code starts here, calls main function
if __name__ == "__main__":
    main() # run main