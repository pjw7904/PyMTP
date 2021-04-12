'''
Author: Peter Willis (pjw7904@rit.edu)

Desc: Test protocol header, demonstrating how you can add custom protocols and their headers
to Scapy.
'''

from scapy.packet import Packet # Importing the super-class of all Scapy protocol headers
from scapy.fields import ( # Importing a couple of pre-made field types
    IntEnumField,
    XByteField,
    ShortField,
    StrField,
    StrLenField,
    ByteField
)

class Disney(Packet):
    name = "Disney" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc= [ 
                    ShortField("mickey",5),
                    XByteField("minnie",3) ,
                    IntEnumField("donald" , 1 , { 1: "happy", 2: "cool" , 3: "angry" }) 
                 ]

# 2 = Testing out strings and length stuff
class Disney2(Packet):
    name = "MTP Path Information" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc= [ 
                    ShortField("Cost", 0),
                    ByteField("Length", None),
                    StrField("Path", "")
                 ]

    def post_build(self, p, pay): # p = current layer, pay = payload
        if self.Length is None:
            pathLen = len(self.Path)
            p = p[:2] + bytes([pathLen]) + p[3:] # Apparently, the fields start counting at 1 for some reason? Maybe I'm looking at this wrong.
        return p