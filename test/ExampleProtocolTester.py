from scapy.all import * # import all of the default scapy library
from ExampleProtocol import Disney, Disney2 # import the custom Disney protocol I defined

def main():
    '''
    # Create a raw packet that contains only a Disney protocol header
    testDisneyPacket = Disney(mickey=3, minnie=20, donald=3)

    # Print out the fields that make up the Disney header
    ls(testDisneyPacket)

    # Print out the raw packet content / what is in the Disney header
    testDisneyPacket.show()
    '''

    testDisney2Packet = Disney2(Cost=69, Path="thisisaprettycooltestIhopethisworksthatwouldbesweet")

    ls(testDisney2Packet)
    testDisney2Packet.show()

    testDisney2Packet.show2()

if __name__ == "__main__":
    main() # run main