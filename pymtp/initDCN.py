'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 07/01/2021
Desc: Defining the starting process/behavior of MTP leaf switches and their inital communication
      with spine switches in a Clos/DCN topology. FOR USE ON GENI, ETH0 IS HARDCODED AS A CTRL PORT
'''
from scapy.all import * # import all of the default scapy library
from mtp import MTP, MTP_Path # import MTP headers
import argparse # for command-line input
import socket # To get interface information, not used for actual sockets
import time

# Set constants for communication
BCAST_ADDR = "01:80:c2:00:00:ff" # Reserved IEEE non-forwarded multicast address


def getLocalInterfaces():
    loopbackIntName = 'lo' # Ubuntu/Linux(?) loopback interface name 
    intToSkip = "eth0"

    interfaceList = socket.if_nameindex() # List which includes interfaces in tuples of format (int#, intName)
    filteredIntList = [int[1] for int in interfaceList if int[1] != intToSkip and int[1] != loopbackIntName] # Filter out the int# and any ints to skip over
    print("ints: ", filteredIntList)
    return filteredIntList


def getLocalMACAddressesFilter():
    macToSkip = "00:00:00:00:00:00"

    MACAddrs = [get_if_hwaddr(i) for i in get_if_list() if get_if_hwaddr(i) != macToSkip]

    filter = ""

    for mac in MACAddrs:
        filter += " not ether src host {0} and".format(mac)

    filter = filter.rstrip("and").strip()

    print("MAC filter:", filter)

    return filter


def sendMTPFrame(MT_PDU, outInt):
    # Send the frame
    sendp(MT_PDU, iface=outInt, count=1, verbose=False)
    
    return


def main():
    # Read in command-line arguments for start-up Meshed Tree Switch configuration, if necessary
    argParser = argparse.ArgumentParser(description = "MTP DCN Init")
    argParser.add_argument('--leaf') # ARG: starting VID
    args = argParser.parse_args()

    # Get the starting VID, if the node is a leaf node   
    rootVID = args.leaf

    # If the node is a LEAF NODE
    if(rootVID):
        leafNodeProcess(rootVID)

    # If the node is a SPINE NODE
    else:
        spineNodeProcess()

    return


def leafNodeProcess(startingVID):
    initVID = MTP_Path(cost=1, path=startingVID)

    # Get the valid interface names and MAC addresses on the node
    intList = getLocalInterfaces()
    MACFilter = getLocalMACAddressesFilter()

    # Define a CPVID data structure (just a dictionary for now)
    CPVIDTable = {}

    # Send root VID information (Hello/Advt) out of each active and valid interface
    for interface in intList:
        intNumber = int(interface.strip("eth")) # Get the int number only, no "eth" in front

        # Define the MTP header, add the VID path, and send it
        MTPFrame = Ether(dst=BCAST_ADDR, type=0x4133)/MTP(type=3, operation=1, port=intNumber, paths=[initVID])
        sendMTPFrame(MTPFrame, interface)


    # Await CPVID information
    sniff(iface=intList, filter=MACFilter, monitor=True, prn=leafResponse(CPVIDTable, startingVID))

    return


def spineNodeProcess():
    # Get the valid interface names and MAC addresses on the node
    intList = getLocalInterfaces()
    MACFilter = getLocalMACAddressesFilter()
    #MACFilter = "not ether src host 02:ea:ba:cf:2c:e4"
    
    # Define a VID data structure (just a dictonary for now)
    VIDTable = {}

    # Await VID information
    sniff(iface=intList, filter=MACFilter, monitor=True, prn=spineResponse(VIDTable))

    return


def leafResponse(CPVIDTable, startingVID):
    def handleFrame(receivedFrame):
        print("hit")
        if(MTP in receivedFrame):
            print("hit")
            if(receivedFrame[MTP].type == 3 and MTP_Path in receivedFrame and receivedFrame[MTP].paths[0].path.decode() == startingVID):
                CPVIDTable[receivedFrame.sniffed_on] = "{0}.{1}".format(receivedFrame[MTP].paths[0].path.decode(), receivedFrame.sniffed_on.strip("eth"))
                print(CPVIDTable)

    return handleFrame


def spineResponse(VIDTable):
    def handleFrame(receivedFrame):
        if(MTP in receivedFrame):
            if(receivedFrame[MTP].type == 3 and MTP_Path in receivedFrame):
                VIDTable[receivedFrame.sniffed_on] = "{0}.{1}".format(receivedFrame[MTP].paths[0].path.decode(), receivedFrame[MTP].port)

                # Update L2 data and resend back to leaf
                receivedFrame[Ether].src = get_if_hwaddr(receivedFrame.sniffed_on)
                receivedFrame[MTP].port = int(receivedFrame.sniffed_on.strip("eth"))
                
                time.sleep(5) # Just as a little test right now
                sendMTPFrame(receivedFrame, receivedFrame.sniffed_on)
                print(VIDTable)

    return handleFrame


if __name__ == "__main__":
    main() # run main