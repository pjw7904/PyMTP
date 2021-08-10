'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 08/09/2021
Desc: The driver/main logic for a Data Center Network based Meshed Tree Protocol (DCN-MTP)
      implementation. This results in a basic, python-based software switch that utilies DCN-MTP.
'''
from MTPSendRecv import * # Transmit, receive, build, and parse MTP messages
from NetUtils import * # Local network configuration information
from socket import socket, AF_PACKET, SOCK_RAW, ntohs # Build raw sockets
from PIDTable import PIDTable # Insert and access DCN-MTP forwarding table
import argparse # Command-line input
import netifaces as ni # Local network/interface information


# Parses the arguments given on the command line (if any)
def parseArgs():
    # Read in command-line arguments for start-up switch configuration, if necessary
    argParser = argparse.ArgumentParser(description = "DCN-MTP Software Switch")
    argParser.add_argument('--leaf') # ARG: starting VID
    args = argParser.parse_args()

    return args # return the results of the given CLI input


# Start of the MTP switch code
def main():
    # Read in command-line arguments to determine if node is a leaf or spine node
    args = parseArgs()

    # Create a raw socket where frames can be received, only MTP Ethertype frames for now to get things going
    s = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_TYPE_MTP))


    if(args.leaf): # If the node is a leaf switch
        leafProcess(args.leaf, s) # Take the host interface name, along with the socket
    else: # If the node is a spine switch
        spineProcess(s) # The spine just needs to take the socket

    return


# The steps taken by a DCN-MTP leaf node
def leafProcess(hostInt, recvSoc):
    # Get necessary interface information to communicate with spine nodes
    spineIntList = getLocalInterfaces()
    spineIntList.remove(hostInt) # Remove the host int, we just want the spine interfaces in this list

    computeSubnetMACAddr = getMACAddress(hostInt) # MAC address of the interface attached to the local IPv4 compute subnet

    # Create a DCN-MTP forwarding table for a LEAF node
    leafTable = PIDTable(len(spineIntList))

    # Determine the LeafID from the host interface
    leafID = ni.ifaddresses(hostInt)[ni.AF_INET][0]['addr'].split(".")[2]

    # Send Leaf Annoucement messages to each spine
    for intf in spineIntList:
        ancmtMsg = buildAnnouncementMsg(int(leafID), intf)
        sendMTPMsg(ancmtMsg, intf)

    # Get aquainted with every spine node before continuing on
    while(spineIntList):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        # If a spine responds with an announcement response
        if(MTPMessageType == MTP_ANNOUNCEMENT):
            # Add the spine as a child to the PID table and print the updated table
            PID = "{0}.{1}".format(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID)
            leafTable.addChild(PID, receivedPort)
            leafTable.getTables()
            spineIntList.remove(receivedPort) # Remove the interface attached to the spine node from the list, as we have heard from it and have a record now in the table
        # If an MTP message is received and we don't know what to do with it
        else:
            print("ERROR: unknown message type")

    # Close the initial socket and open a new one that listens for all traffic
    recvSoc.close()
    clientSoc = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_P_ALL)) # Cannot just listen on IP, we need MTP-routed frames as well
    
    # Loop through the switching logic until the switch is shut down (cntrl + c)
    print("looking for client traffic")
    while(True):
        message, socketData = clientSoc.recvfrom(RECV_BUF_SIZE) # Receive a frame
        receivedPort = socketData[0] # Determine the interface the frame came from

        # Ignore frames from the GENI control interface
        if(receivedPort == "eth0"):
            continue
        
        # Have Scapy process and parse the frame
        receivedFrame = Ether(message)
        
        # Determine what to do with the frame based on the encapsulated type (ethertype)
        if(MTP in receivedFrame and receivedFrame[MTP].type == MTP_ROUTED): # If the frame is an MTP routed frame
            # If the destination leaf ID is the local leaf ID
            if(receivedFrame[MTP].dstleafID == int(leafID)):
                print("received an MTP message going to my IPv4 subnet:")
                receivedFrame.show2()

                # Deencapsulate the MTP header and send it to the local compute node
                decapedFrame = Ether(src=computeSubnetMACAddr)/receivedFrame[IP]
                print("sending the following de-encapsulated packet to compute node:")
                decapedFrame.show2()
                sendMTPMsg(decapedFrame, hostInt)

        elif(IP in receivedFrame and receivedFrame[Ether].src != computeSubnetMACAddr): # If the frame contains an IPv4 header (packet sent by compute node attached to leaf)
            print("received client frame:")
            receivedFrame.show2()

            # Determine what the destination leaf ID is and which spine it is being sent to (flows based on src + dst IPv4 address, which are hashed)
            sourceIP = receivedFrame[IP].src
            destinationIP = receivedFrame[IP].dst
            destinationLeafID = int(getLeafIDFromIPAddress(receivedFrame[IP].dst))
            egressInt = leafTable.getEgressSpinePort(sourceIP, destinationIP)

            # Craft an MTP routed message (encapsulate compute node IPv4 packet in MTP routed header) to send out of the chosen interface
            encapedFrame = Ether(src=getMACAddress(egressInt), dst=DEST_MTP_PHY_ADDR)/MTP(type=MTP_ROUTED, srcleafID=int(leafID), dstleafID=destinationLeafID)/receivedFrame[IP]
            print("encapsulated client frame:")
            encapedFrame.show2()

            # Send the MTP routed message out of the chosen egress interface/to the chosen spine node
            sendMTPMsg(encapedFrame, egressInt)

        else: # If the frame does not contain an MTP routed header or an IPv4 header, we're ignoring for now
            print("ERROR: Ethertype not MTP or IPv4, frame dropped")

    return


# The steps taken by a DCN-MTP spine node
def spineProcess(recvSoc):
    # Get the valid interface names on the node
    intList = getLocalInterfaces()

    # Create a DCN-MTP forwarding table for a SPINE node
    spineTable = PIDTable(len(intList))

    # Loop through the switching logic until the switch is shut down (cntrl + c)
    switchIsActive = True
    while(switchIsActive):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        # If a leaf sends an announcement response
        if(MTPMessageType == MTP_ANNOUNCEMENT):
            # Add leaf annoucement information as a parent to MTP table (cost of 1 hard-coded for now)
            spineTable.addParent(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID, 1, receivedPort)
            spineTable.getTables()

            # Send the annoucement back as a confirmation
            response = buildAnnoucementResponseMsg(receivedFrame, receivedPort)
            sendMTPMsg(response, receivedPort)

        # If a leaf sends a frame with a routed MTP header
        elif(MTPMessageType == MTP_ROUTED):
            # Print out the frame to see what is inside
            print("received MTP-encaped message:")
            receivedFrame.show2()
            
            # Determine the egress interface (the leaf to send it to) based on the destination leaf ID field
            outIntf = spineTable.getEgressLeafPort(receivedFrame[MTP].dstleafID)
            if(outIntf != "None"):
                print("message routed out of port", outIntf)
                routeMsg(receivedFrame, outIntf)
            else:
                print("Error: No route to destination leaf")

    return


# Switch code starts here, calls main function
if __name__ == "__main__":
    main() # run main