import sys
sys.path.append("../pymtp")

from scapy.all import * # import all of the default scapy library
from socket import socket, AF_PACKET, SOCK_RAW, ntohs # Build raw sockets
from mtp import MTP # import MTP headers

# Constants used in setting up the socket
ETH_P_ALL = 0x0003 # Receive all traffic, regardless of ethertype
RECV_BUF_SIZE = 4096 # Take in 4096 bytes for each socket recv call
DEST_MTP_PHY_ADDR = "01:80:c2:00:00:ff"
DEFAULT_EGRESS_INTF = "eth1"


# Set up the socket which will be used to send (not receive) frames
def sendFrame(message, interface):
    sendSoc = socket(AF_PACKET, SOCK_RAW)
    sendSoc.bind((interface, 0))

    message = bytes(message)
    return sendSoc.send(message)


def main():
    # Set up the socket which will be used to receive (not send) frames
    recvSoc = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_P_ALL))

    # Build an MTP message
    spineIDs = [5, 1, 7]
    MTPFrame = Ether(dst=DEST_MTP_PHY_ADDR, type=0x4133)/MTP(type=1, leafID=1, spineID=spineIDs)

    # Send a test frame
    sendFrame(MTPFrame, DEFAULT_EGRESS_INTF)

    while(True):
        message, socketData = recvSoc.recvfrom(RECV_BUF_SIZE) # Receive a frame
        receivedPort = socketData[0] # Determine the interface the frame came from

        # Ignore frames from the GENI control interface
        if(receivedPort == "eth0"):
            continue
            
        # Have Scapy process and parse the frame
        receivedFrame = Ether(message)
        receivedFrame.show2()


if __name__ == "__main__":
    main() # run main