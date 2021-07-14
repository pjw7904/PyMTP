'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 06/03/2021
Desc: A basic script to test a basic MT_VID propogation system. To be used on Mininet, GENI, 
      or any network of Scapy-installed devices. Currently DOES NOT work for Scapy 2.4.5, use 2.4.4.
'''
import sys
sys.path.append("../pymtp")

from scapy.all import * # import all of the default scapy library
from mtp import MTP, MTP_Path # import MTP headers
import argparse # for command-line input
import socket # To get interface information, not used for actual sockets


def getLocalInterfaces(intToSkip):
    loopbackIntName = 'lo' # Ubuntu/Linux(?) loopback interface name 

    interfaceList = socket.if_nameindex() # List which includes interfaces in tuples of format (int#, intName)
    filteredIntList = [int[1] for int in interfaceList if int[1] != intToSkip and int[1] != loopbackIntName] # Filter out the int# and any ints to skip over
    return filteredIntList


def sendMTPFrame(MT_PDU, outInt):
    # Send the frame
    sendp(MT_PDU, iface=outInt, count=1, verbose=False)
    
    return


def respondToMTPFrame(receivedFrame):
    frameInfo = "TBA" # String describing the recieved frame information

    if(MTP in receivedFrame): # If there is an MTP header in the frame, continue on
        print("Received MT_PDU information:")

        frameInfo = "type = unknown"

        # Determine the type of MT_PDU being received
        if(receivedFrame[MTP].type == 1):
            frameInfo = "Type = 1 (Hello)"

        elif(receivedFrame[MTP].type == 2):
            frameInfo = "Type = 2 (Join)"

        # If the MT_PDU is an advt, print out the information inside of it
        elif(receivedFrame[MTP].type == 3):
            frameInfo = """
                        Type = 3 (Path Bundle Advertisement)
                        Operation = {0}
                        from port: {1}
                        number of paths included: {2}
                        path info:
                        """.format(receivedFrame[MTP].operation, receivedFrame[MTP].port, 
                                   receivedFrame[MTP].count)
            
            # Print out each path (and its info) in the included advt path bundle, note how Scapy can iterate over PacketLists
            pathNo = 1
            for path in receivedFrame[MTP].paths:
                frameInfo = frameInfo + "--Path {0}--\nCost = {1}\nLength = {2}\nPath = {3}".format(pathNo, path.cost, path.length, path.path)
                pathNo += 1
    
    # if a frame that is not an MT_PDU is received, let the user know and stop
    else:
        frameInfo = "Frame recieved, does not contain an MTP header"

    # Print out the frame information (regardless if it is an MT_PDU)
    print(frameInfo)

    return


def main():
    # Set constants for communication
    # The multicast addr (01:80:C2:00:00:0F) isn't picked up for sniff(), so just all ffs for now
    broadcastAddr = "01:80:c2:00:00:ff" # Reserved IEEE non-forwarded multicast address

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
        # Defining a path bundle to send with three paths, one real(ish), two made up randomly
        initVID = MTP_Path(cost=1, path=rootVID)
        path2   = MTP_Path(cost=3, path="1.1.2.3")
        path3   = MTP_Path(cost=4, path="1.2.4.3")

        # Group the individual path headers into a list
        pathBundlePathHeaders = [initVID, path2, path3]

        # Send path bundle information out of each active and valid (non-control) interface
        for interface in intList:
            intNumber = int(interface.strip("eth")) # Get the int number only, no "eth" in front
            # Define the MTP header, add the path bundle paths, and send it
            MTPFrame = Ether(dst=broadcastAddr, type=0x4133)/MTP(type=3, operation=1, port=intNumber, paths=pathBundlePathHeaders)
            sendMTPFrame(MTPFrame, interface)
            print("sent MT_PDU out of interface {0}, which is port number {1}".format(interface, intNumber))

    else:
        # NOTE: Scapy ver. 2.4.5 has a bug which does not allow for multi-int sniffing, use 2.4.4
        sniff(iface=intList, monitor=True, prn=respondToMTPFrame)


if __name__ == "__main__":
    main() # run main