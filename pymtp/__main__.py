from socket         import socket, AF_PACKET, SOCK_RAW, ntohs # Build raw sockets
from signal         import signal, SIGINT                     # Signal associated with a control + c exit of program
from sys            import exit                               # Graceful exit upon SIGINT signal (cntrl+c)
from MTP_switch     import leafProcess, spineProcess
from MTPSendRecv    import ETH_TYPE_MTP

import logging  # Basic level-based logging
import argparse # Command-line input


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
    argParser.add_argument("-t", "--top", action='store_true')
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
        spineProcess(s, args.top) # The spine needs to take the socket and whether it is the top of the folded-Clos

    return

# Switch code starts here, calls main function
if __name__ == "__main__":
    main() # run main