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
    fields_desc=[
                  ShortField("cost", None),
                  FieldLenField("length", None, length_of="path"),
                  StrLenField("path", NULL_PATH, length_from=lambda pkt:pkt.length)
                ] 

    def extract_padding(self, s):
        return '', s


class MTP(Packet):
    name = "Meshed Tree Protocol" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc= [ 
                    ByteEnumField("type", UNKNOWN, MTP_Types),
                    ConditionalField(ByteEnumField("operation", UNKNOWN, MTP_Advt_Operations), lambda pkt:pkt.type == ADVT_TYPE),
                    ConditionalField(ShortField("port", UNKNOWN), lambda pkt:pkt.type == ADVT_TYPE),
                    ConditionalField(FieldLenField("count", None, count_of="paths"), lambda pkt:pkt.type == ADVT_TYPE), # THIS CANNOT BE ZERO, IT HAS TO BE NONE TO WORK
                    ConditionalField(PacketListField("paths", [], MTP_Path, count_from=lambda pkt:pkt.count), lambda pkt:pkt.type == ADVT_TYPE)
                 ]

bind_layers(Ether, MTP, type=0x4133)
bind_layers(MTP, MTP_Path, type=ADVT_TYPE)
bind_layers(MTP_Path, MTP_Path)