from mtp import TEST
from scapy.all import *
import sys

OUTGOING_INTF = "eth1" # For GENI use. Clients will only be connected to one machine, hence eth1

'''
Just turn off IP routing statck?
'''

def main():
    testing = Ether()/IP(dst=sys.argv[1])/UDP(sport=28, dport=28)/TEST(seqnum=1)
    testing.show2()
    sendp(testing, iface=OUTGOING_INTF, count=1, verbose=False)
    return


if __name__ == "__main__":
    main() # run main