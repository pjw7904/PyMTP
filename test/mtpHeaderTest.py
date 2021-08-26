import sys
sys.path.append("../pymtp")

from scapy.all import * # import all of the default scapy library
from mtp import MTP, TEST # import MTP header and traffic generator header

def main():
    ls(MTP)

    # Testing control plane header
    spineIDs = [5, 7, 1] # Hypothetical Clos topology with 3 tiers of spines
    testCPMTPFrame = Ether()/MTP(type=1, leafID=1, spineID=spineIDs)
    testCPMTPFrame.show()
    testCPMTPFrame.show2()

    print("Printing out individual tier IDs:")
    print(testCPMTPFrame[MTP].spineID[0])
    print(testCPMTPFrame[MTP].spineID[1])
    print(testCPMTPFrame[MTP].spineID[2])

    # testing data plane header and traffic generator header
    testDPMTPFrame = Ether()/MTP(type=9, srcleafID=120, dstleafID=130)/IP(src="192.168.2.5",dst="192.168.1.2")/UDP(sport=28, dport=28)/TEST(seqnum=25)
    testDPMTPFrame.show()
    testDPMTPFrame.show2()

if __name__ == "__main__":
    main() # run main