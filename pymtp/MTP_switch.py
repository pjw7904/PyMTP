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
import logging # Basic level-based logging
#import netifaces as ni # Local network/interface information


# The steps taken by a DCN-MTP leaf node
def leafProcess(hostInt):
    # Before communicating in the DCN-MTP routed core, you need to hear from AT LEAST one spine node
    spineDiscovered = False

    # Set up the socket which will be used to receive (not send) frames
    leafSoc = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_P_ALL))

    # Get necessary interface information to communicate with spine nodes
    spineIntList = getLocalInterfaces()
    spineIntList.remove(hostInt)

    # Get host interface information
    computeSubnetMACAddr = getMACAddress(hostInt) # MAC address of the interface attached to the local IPv4 compute subnet
    computeSubnetIPv4Addr = getIPv4Address(hostInt) # IPv4 address of the interface attached to the local IPv4 compute subnet
    computeSubnetIPv4Mask = getIPv4NetMask(hostInt) # IPv4 network mask of compute subnet interface

    # Create a DCN-MTP forwarding table for a LEAF node and add the compute interface to it
    leafTable = PIDTable(getLocalInterfaces())
    leafTable.addComputeSubnet(computeSubnetIPv4Addr, computeSubnetIPv4Mask, hostInt)

    # Determine the LeafID from the host 
    leafID = int(computeSubnetIPv4Addr.split(".")[2])

    # Send Leaf Annoucement messages to each potential spine node
    spineIntfMACAddrs = []
    for intf in spineIntList:
        spineIntfMACAddrs.append(getMACAddress(intf))
        ancmtMsg = buildAnnouncementMsg(leafID, intf)
        sendMTPMsg(ancmtMsg, intf)
        logging.info("\n[sent - {0}] Announcing myself to potential spine".format(intf))
        logging.debug("\n" + ancmtMsg.show2(dump=True))

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
            if(receivedFrame[MTP].type == MTP_ANNOUNCEMENT and receivedFrame[MTP].leafID == leafID and receivedFrame[MTP].annoucementType == ANCMT_RES and receivedFrame[Ether].src not in spineIntfMACAddrs):
                # Add the spine as a child to the PID table and print the updated table
                leafTable.addChild(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID,  receivedPort)
                
                logging.info("\n[recv - {0}] Announcement confirmation from spine {1}, adding child".format(receivedPort, leafTable.getChildPID(receivedPort)))
                logging.debug("\n" + receivedFrame.show2(dump=True))
                logging.info(leafTable.getTables())

            elif(receivedFrame[MTP].type == MTP_ROUTED and receivedFrame[MTP].dstleafID == leafID):
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
            
            egressInt = leafTable.getEgressUpstreamInterface(sourceIP, destinationIP)
            # If a valid egress interface is found
            if(egressInt != "None"):
                # Craft an MTP routed message (encapsulate compute node IPv4 packet in MTP routed header) to send out of the chosen interface
                encapedFrame = Ether(src=getMACAddress(egressInt), dst=DEST_MTP_PHY_ADDR)/MTP(type=MTP_ROUTED, srcleafID=leafID, dstleafID=destinationLeafID)/receivedFrame[IP]

                # Send the MTP routed message out of the chosen egress interface/to the chosen spine node
                sendMTPMsg(encapedFrame, egressInt)
                logging.info("[sent - {0}] Sending MTP-encaped compute node frame to a spine:".format(egressInt))
                logging.info(encapedFrame.summary())
                logging.debug("\n" + encapedFrame.show2(dump=True))

            # If there is no valid egress interface 
            else:
                logging.info("\n[notice] No upstream spines available to route to, msg dropped")

        '''else: # If the frame does not contain an MTP routed header or an IPv4 header, we're ignoring for now
            print("\nERROR: Ethertype not MTP or IPv4, frame dropped")'''

    return


# The steps taken by a DCN-MTP spine node
def spineProcess(recvSoc, isTopTier):
    # Get the valid interface names on the node
    intList = getLocalInterfaces()

    # Create a DCN-MTP forwarding table for a SPINE node
    spineTable = PIDTable(getLocalInterfaces())

    # Loop through the switching logic until the switch is shut down (cntrl + c)
    switchIsActive = True
    while(switchIsActive):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive an MTP message
        receivedFrame = Ether(message) # Parse message to Scapy formatting
        receivedPort = socketData[0] # Determine ingress port

        MTPMessageType = receivedFrame[MTP].type # Determine the type of MTP message received

        # If a leaf sends an announcement response
        if(MTPMessageType == MTP_ANNOUNCEMENT):
            if(receivedFrame[MTP].annoucementType == ANCMT_REQ):
                # Add leaf annoucement information as a parent to MTP table (cost of 1 hard-coded for now)
                spineTable.addParent(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID, 1, receivedPort)
                
                logging.info("\n[recv - {0}] Receieved an announcement request from a downstream node, adding parent".format(receivedPort))
                logging.info(receivedFrame.summary())
                logging.debug("\n" + receivedFrame.show2(dump=True))
                logging.info(spineTable.getTables())

                # Send the annoucement back as a confirmation
                response = buildAnnoucementResponseMsg(receivedFrame, receivedPort)
                sendMTPMsg(response, receivedPort)
                
                if(not isTopTier):
                    logging.info("[sent - {0}] Announcing myself back to the downstream node".format(receivedPort))
                    logging.debug("\n" + response.show2(dump=True))

                    # Send an updated path vector to upstream nodes
                    for intf in spineTable.getNonComputeInterfaces():
                        if(intf != receivedPort):
                            ancmtMsg = buildAnnouncementMsg(receivedFrame[MTP].leafID, intf, multipleIDs=receivedFrame[MTP].spineID)
                            sendMTPMsg(ancmtMsg, intf)
                            
                            logging.info("\n[sent - {0}] Announcing myself to potential super spine".format(intf))
                            logging.debug("\n" + ancmtMsg.show2(dump=True))

           
            elif(receivedFrame[MTP].annoucementType == ANCMT_RES):
                # Add the spine as a child to the PID table and print the updated table
                spineTable.addChild(receivedFrame[MTP].leafID, receivedFrame[MTP].spineID, receivedPort)
                
                logging.info("\n[recv - {0}] Received an announcement reply from upstream node {1}, adding child".format(receivedPort, spineTable.getChildPID(receivedPort)))
                logging.debug("\n" + receivedFrame.show2(dump=True))
                logging.info(spineTable.getTables())

        # If a leaf sends a frame with a routed MTP header
        elif(MTPMessageType == MTP_ROUTED):
            # Print out the frame to see what is inside
            logging.info("\n[recv - {0}] Received an MTP-encaped msg:".format(receivedPort))
            logging.info(receivedFrame.summary())
            logging.debug("\n" + receivedFrame.show2(dump=True))

            # Determine the egress interface based on the (maybe source and) destination leaf ID field
            outIntf = spineTable.getEgressInterface(receivedFrame[MTP].srcleafID, receivedFrame[MTP].dstleafID)
            if(outIntf != "None"):
                routeMsg(receivedFrame, outIntf)
                logging.info("\n[sent - {0}] Msg routed towards destination".format(outIntf))
            else:
                logging.info("\n[notice] No route to destination leaf")

    return

