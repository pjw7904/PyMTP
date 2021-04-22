'''
Author: Peter Willis (pjw7904@rit.edu)

Desc: The protocol header for the Meshed Tree Protocol (MTP), which is the control-plane protocol which
      builds meshed trees on a network.
'''

from scapy.packet import bind_layers, Packet # Importing the super-class of all Scapy protocol headers
from scapy.layers.l2 import Ether # Importing the Ethernet II header for binding to the MTP header
from scapy.fields import (      # Importing a couple of pre-made field types
    ByteField,
    ByteEnumField,
    ShortField,
    StrField,
    StrLenField,
    PacketListField,
    FieldLenField,
    ConditionalField,
    IntField
)

# Constants for MTP header information to give more context to default field parameters
UNKNOWN   = 0
ADVT_TYPE = 3
NULL_PATH = ""

MTP_Types = {
    0: "Unknown",
    1: "Hello",
    2: "Join",
    3: "Path Bundle Advertisement"
}

MTP_Advt_Operations = {
    0: "Unknown Operation",
    1: "Path Additions",
    2: "Path Deletions"
}


class MTP_Path(Packet):
    name = "MTP Path Information" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc= [ 
                    ShortField("Cost", None),
                    ByteField("Length", None),
                    StrField("Path", None)
                 ]

    def extract_padding(self, s):
        return '', s
    
    def post_build(self, p, pay): # After path header is built, calculate length of path
        if self.Length is None:
            pathLen = len(self.Path)
            p = p[:2] + bytes([pathLen]) + p[3:]
        return p


class MTP(Packet):
    name = "Meshed Tree Protocol" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc= [ 
                    ByteEnumField("type", UNKNOWN, MTP_Types),
                    ConditionalField(ByteEnumField("Operation", UNKNOWN, MTP_Advt_Operations), lambda pkt:pkt.type == ADVT_TYPE),
                    ConditionalField(FieldLenField("Count", None, count_of="Paths"), lambda pkt:pkt.type == ADVT_TYPE), # THIS CANNOT BE ZERO, IT HAS TO BE NONE TO WORK
                    ConditionalField(PacketListField("Paths", [], MTP_Path, count_from=lambda pkt:pkt.Count), lambda pkt:pkt.type == ADVT_TYPE)
                 ]

bind_layers(Ether, MTP, type=0x4133)
bind_layers(MTP, MTP_Path, type=ADVT_TYPE)
bind_layers(MTP_Path, MTP_Path)