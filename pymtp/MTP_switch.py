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
    # Get necessary interface information
    intList = getLocalInterfaces()
    intList.remove(hostInt) # We don't want to look at this right now, just spine ints
    computeSubnetMACAddr = getMACAddress(hostInt) # MAC address of the interface attached to the local IPv4 compute subnet

    # Create a DCN-MTP forwarding table for a LEAF node
    leafTable = PIDTable(len(intList))

    # Determine LeafID from the host interface
    leafID = ni.ifaddresses(hostInt)[ni.AF_INET][0]['addr'].split(".")[2]

    # Send Leaf Annoucement messages to each spine
    for intf in intList:
        ancmtMsg = buildAnnouncementMsg(int(leafID), intf)
        sendMTPMsg(ancmtMsg, intf)

    # Get aquainted with every spine node before continuing on
    while(intList):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        if(MTPMessageType == MTP_ANNOUNCEMENT):
            PID = "{0}.{1}".format(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID)
            leafTable.addChild(PID, receivedPort)
            leafTable.getTables()
            intList.remove(receivedPort)
        else:
            print("ERROR: unknown message type")

    recvSoc.close()
    clientSoc = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_P_ALL)) # Cannot just listen on IP, we need MTP-routed frames as well!
    
    print("looking for client traffic")
    while(True):
        message, socketData = clientSoc.recvfrom(RECV_BUF_SIZE)
        receivedPort = socketData[0]

        if(receivedPort == "eth0"):
            continue
        
        # Have Scapy process and parse the frame (show it for now to test it)
        receivedFrame = Ether(message)
        
        # Determine what to do with the frame based on the encapsulated type
        if(MTP in receivedFrame and receivedFrame[MTP].type == MTP_ROUTED):
            if(receivedFrame[MTP].dstleafID == int(leafID)):
                print("received an MTP message going to my IPv4 subnet:")
                receivedFrame.show2()

                decapedFrame = Ether(src=computeSubnetMACAddr)/receivedFrame[IP]
                print("sending the following de-encapsulated packet to compute node:")
                decapedFrame.show2()

                sendMTPMsg(decapedFrame, hostInt)

        elif(IP in receivedFrame and receivedFrame[Ether].src != computeSubnetMACAddr):
            print("received client frame:")
            receivedFrame.show2()

            # Figure out the interface the packet is going out of
            sourceIP = receivedFrame[IP].src
            destinationIP = receivedFrame[IP].dst
            destinationLeafID = int(getLeafIDFromIPAddress(receivedFrame[IP].dst))
            egressInt = leafTable.getEgressSpinePort(sourceIP, destinationIP)

            # Craft an MTP routed message to send out of the chosen interface
            encapedFrame = Ether(src=getMACAddress(egressInt), dst=DEST_MTP_PHY_ADDR)/MTP(type=MTP_ROUTED, srcleafID=int(leafID), dstleafID=destinationLeafID)/receivedFrame[IP]
            print("encapsulated client frame:")
            encapedFrame.show2()

            # Send the MTP routed message out of the chosen egress interface
            sendMTPMsg(encapedFrame, egressInt)

        else:
            print("ERROR: Ethertype not MTP or IPv4, frame dropped")

    return


def spineProcess(recvSoc):
    # Get the valid interface names on the node
    intList = getLocalInterfaces()

    # Create a DCN-MTP forwarding table for a SPINE node
    spineTable = PIDTable(len(intList))

    # Loop through the switching logic until the switch is shut down
    switchIsActive = True
    while(switchIsActive):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received
        if(MTPMessageType == MTP_ANNOUNCEMENT):
            '''
            TODO: Add check if leaf sends another ancmt with same OR new info to replace what is there.
                  Or, just make default entries for each port and then update them for whats incoming.
            '''
            # Add leaf annoucement information as a parent to MTP table (cost of 1 hard-coded for now)
            spineTable.addParent(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID, 1, receivedPort)
            spineTable.getTables()

            # Send the ancmt back as a confirmation
            response = buildAnnoucementResponseMsg(receivedFrame, receivedPort)
            sendMTPMsg(response, receivedPort)

        elif(MTPMessageType == MTP_ROUTED):
            print("received MTP-encaped message:")
            receivedFrame.show2()
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