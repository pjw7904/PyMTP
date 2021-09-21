'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 09/21/2021
Desc: The driver/main logic for a Data Center Network based Meshed Tree Protocol (DCN-MTP)
      implementation. This results in a basic, python-based software switch that utilies DCN-MTP.
'''
from MTPSendRecv import * # Transmit, receive, build, and parse MTP messages
from NetUtils import * # Local network configuration information
from socket import socket, AF_PACKET, SOCK_RAW, ntohs # Build raw sockets
from PIDTable import PIDTable # Insert and access DCN-MTP forwarding table
from signal import signal, SIGINT # Signal associated with a control + c exit of program
from sys import exit # Graceful exit upon SIGINT signal (cntrl+c)
import argparse # Command-line input
import logging # Basic level-based logging
import netifaces as ni # Local network/interface information


# Handles SIGINT (control + c) and exits gracefully
def handler(signal_received, frame):
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)


# Parses the arguments given on the command line (if any)
def parseArgs():
    # Read in command-line arguments for start-up switch configuration, if necessary
    argParser = argparse.ArgumentParser(description = "DCN-MTP Software Switch")
    argParser.add_argument('--leaf') # ARG: starting VID
    argParser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help="Set the logging level (default: %(default)s)")
    args = argParser.parse_args()

    return args # return the results of the given CLI input


# Start of the MTP switch code
def main():
    # Connect signals to the local handler (for control + c termination)
    signal(SIGINT, handler)

    # Read in command-line arguments
    args = parseArgs()

    # Determine the level of logging that will be included when running
    logging.basicConfig(level=getattr(logging, args.logLevel))

    # Create a raw socket where frames can be received, only MTP Ethertype frames for now to get things going
    s = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_TYPE_MTP))


    if(args.leaf): # If the node is a leaf switch
        leafProcess(args.leaf) # Take the host interface name, along with the socket
    else: # If the node is a spine switch
        spineProcess(s) # The spine just needs to take the socket

    return


# The steps taken by a DCN-MTP leaf node
def leafProcess(hostInt):
    # Before communicating in the DCN-MTP routed core, you need to hear from AT LEAST one spine node
    spineDiscovered = False

    # Set up the socket which will be used to receive (not send) frames
    leafSoc = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_P_ALL))

    # Get necessary interface information to communicate with spine nodes
    spineIntList = getLocalInterfaces()
    spineIntList.remove(hostInt) # Remove the host int, we just want the spine interfaces in this list

    computeSubnetMACAddr = getMACAddress(hostInt) # MAC address of the interface attached to the local IPv4 compute subnet

    # Create a DCN-MTP forwarding table for a LEAF node
    leafTable = PIDTable()

    # Determine the LeafID from the host interface
    leafID = ni.ifaddresses(hostInt)[ni.AF_INET][0]['addr'].split(".")[2]

    # Send Leaf Annoucement messages to each potential spine node
    spineIntfMACAddrs = []
    for intf in spineIntList:
        spineIntfMACAddrs.append(getMACAddress(intf))
        ancmtMsg = buildAnnouncementMsg(int(leafID), intf)
        sendMTPMsg(ancmtMsg, intf)
        logging.info("\n[sent - {0}] Announcing myself to potential spine".format(intf))

    # Loop through the switching logic until the switch is shut down (cntrl + c)
    logging.info("\n~Begin listening and responding~")
    while(True):
        message, socketData = leafSoc.recvfrom(RECV_BUF_SIZE) # Receive a frame
        receivedPort = socketData[0] # Determine the interface the frame came from

        # Ignore frames from the GENI control interface
        if(receivedPort == "eth0"):
            continue
        
        # Have Scapy process and parse the frame
        receivedFrame = Ether(message)
        
        # Determine what to do with the frame based on the encapsulated type (ethertype)
        if(MTP in receivedFrame):
            if(receivedFrame[MTP].type == MTP_ANNOUNCEMENT and receivedFrame[Ether].src not in spineIntfMACAddrs):
                # Add the spine as a child to the PID table and print the updated table
                PID = "{0}.{1}".format(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID[0])
                leafTable.addChild(PID, receivedPort)
                logging.info("\n[recv - {0}] Announcement confirmation from spine {1}, adding child".format(receivedPort, PID))
                logging.debug("\n" + receivedFrame.show2(dump=True))
                logging.info(leafTable.getTables())

            elif(receivedFrame[MTP].type == MTP_ROUTED and receivedFrame[MTP].dstleafID == int(leafID)):
                logging.info("\n[recv - {0}] Received MTP-encaped msg for the local leaf ID:".format(receivedPort))
                logging.info(receivedFrame.summary())
                logging.debug("\n" + receivedFrame.show2(dump=True))

                # Deencapsulate the MTP header and send it to the local compute node
                decapedFrame = Ether(src=computeSubnetMACAddr)/receivedFrame[IP]
                sendMTPMsg(decapedFrame, hostInt)
                logging.info("[sent - {0}] Msg sent to local compute node".format(hostInt))
                logging.info(decapedFrame.summary())
                logging.debug("\n" + decapedFrame.show2(dump=True))

        elif(IP in receivedFrame and receivedFrame[Ether].src != computeSubnetMACAddr): # If the frame contains an IPv4 header (packet sent by compute node attached to leaf)
            logging.info("\n[recv - {0}] Received frame from a local compute node:".format(receivedPort))
            logging.info(receivedFrame.summary())
            logging.debug("\n" + receivedFrame.show2(dump=True))

            # Determine what the destination leaf ID is and which spine it is being sent to (flows based on src + dst IPv4 address, which are hashed)
            sourceIP = receivedFrame[IP].src
            destinationIP = receivedFrame[IP].dst
            destinationLeafID = int(getLeafIDFromIPAddress(receivedFrame[IP].dst))
            egressInt = leafTable.getEgressSpinePort(sourceIP, destinationIP)

            # Craft an MTP routed message (encapsulate compute node IPv4 packet in MTP routed header) to send out of the chosen interface
            encapedFrame = Ether(src=getMACAddress(egressInt), dst=DEST_MTP_PHY_ADDR)/MTP(type=MTP_ROUTED, srcleafID=int(leafID), dstleafID=destinationLeafID)/receivedFrame[IP]

            # Send the MTP routed message out of the chosen egress interface/to the chosen spine node
            sendMTPMsg(encapedFrame, egressInt)
            logging.info("[sent - {0}] Sending MTP-encaped compute node frame to a spine:".format(egressInt))
            logging.info(encapedFrame.summary())
            logging.debug("\n" + encapedFrame.show2(dump=True))

        '''else: # If the frame does not contain an MTP routed header or an IPv4 header, we're ignoring for now
            print("\nERROR: Ethertype not MTP or IPv4, frame dropped")'''

    return


# The steps taken by a DCN-MTP spine node
def spineProcess(recvSoc):
    # Get the valid interface names on the node
    intList = getLocalInterfaces()

    # Create a DCN-MTP forwarding table for a SPINE node
    spineTable = PIDTable()

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
            spineTable.addParent(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID[0], 1, receivedPort)
            logging.info("\n[recv - {0}] Receieved an announcement from a leaf, adding parent".format(receivedPort))
            logging.info(receivedFrame.summary())
            logging.debug("\n" + receivedFrame.show2(dump=True))
            logging.info(spineTable.getTables())

            # Send the annoucement back as a confirmation
            response = buildAnnoucementResponseMsg(receivedFrame, receivedPort)
            sendMTPMsg(response, receivedPort)
            logging.info("[sent - {0}] Announcing myself back to the leaf".format(receivedPort))
            logging.debug("\n" + response.show2(dump=True))

        # If a leaf sends a frame with a routed MTP header
        elif(MTPMessageType == MTP_ROUTED):
            # Print out the frame to see what is inside
            logging.info("\n[recv - {0}] Received an MTP-encaped msg:".format(receivedPort))
            logging.info(receivedFrame.summary())
            logging.debug("\n" + response.show2(dump=True))

            # Determine the egress interface (the leaf to send it to) based on the destination leaf ID field
            outIntf = spineTable.getEgressLeafPort(receivedFrame[MTP].dstleafID)
            if(outIntf != "None"):
                routeMsg(receivedFrame, outIntf)
                logging.info("\n[sent - {0}] Msg routed towards destination".format(outIntf))
            else:
                logging.info("\nError: No route to destination leaf")

    return


# Switch code starts here, calls main function
if __name__ == "__main__":
    main() # run main