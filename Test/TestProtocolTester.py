from scapy.all import * # import all of the default scapy library
from TestProtocol import Disney # import the custom Disney protocol I defined

def main():
    # Create a raw packet that contains only a Disney protocol header
    testDisneyPacket = Disney(mickey=3, minnie=20, donald=3)

    # Print out the fields that make up the Disney header
    ls(testDisneyPacket)

    # Print out the raw packet content / what is in the Disney header
    testDisneyPacket.show()

if __name__ == "__main__":
    main() # run main