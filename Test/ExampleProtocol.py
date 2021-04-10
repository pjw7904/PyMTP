'''
Author: Peter Willis (pjw7904@rit.edu)

Desc: Test protocol header, demonstrating how you can add custom protocols and their headers
to Scapy.
'''

from scapy.packet import Packet # Importing the super-class of all Scapy protocol headers
from scapy.fields import ( # Importing a couple of pre-made field types
    IntEnumField,
    XByteField,
    ShortField
)

class Disney(Packet):
    name = "Disney" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc=[ ShortField("mickey",5),
                 XByteField("minnie",3) ,
                 IntEnumField("donald" , 1 ,
                      { 1: "happy", 2: "cool" , 3: "angry" } ) ]