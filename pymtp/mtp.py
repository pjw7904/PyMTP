'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 04/28/2021
Desc: The protocol header for the Meshed Tree Protocol (MTP), which is the control-plane protocol which
      builds meshed trees on a network.
'''

from scapy.packet import bind_layers, Packet # Importing the super-class of all Scapy protocol headers
from scapy.layers.l2 import Ether, SourceMACField # Importing Ethernet II header and MAC field
from scapy.layers.inet import IP, UDP
from scapy.fields import (      # Importing a couple of pre-made field types
    ByteEnumField,
    ShortField,
    ConditionalField,
    LongField,
    FieldLenField,
    FieldListField
)

# Constants for MTP header information to give more context to default field parameters
UNKNOWN   = 0
ANCMT_TYPE = 1 # Annoucement message header type value
DP_TYPE = 9 # Data plane header type value

# MTP control plane header types
MTP_Types = {
    0: "Unknown",
    1: "Announcement",
    9: "routed"
}


class TEST(Packet):
    name = "Client Traffic Generator Protocol"

    fields_desc = [
         SourceMACField("src"),
         LongField("seqnum", UNKNOWN)
    ]


class MTP(Packet):
    name = "Meshed Tree Protocol" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc= [ 
                    ByteEnumField("type", UNKNOWN, MTP_Types),
                    ConditionalField(ShortField("leafID", UNKNOWN), lambda pkt:pkt.type == ANCMT_TYPE),
                    ConditionalField(FieldLenField("tierIDCount", None, count_of="spineID"), lambda pkt:pkt.type == ANCMT_TYPE),
                    ConditionalField(FieldListField("spineID", [], ShortField("id", UNKNOWN), count_from=lambda pkt:pkt.tierIDCount), lambda pkt:pkt.type == ANCMT_TYPE),
                    ConditionalField(ShortField("srcleafID", UNKNOWN), lambda pkt:pkt.type == DP_TYPE),
                    ConditionalField(ShortField("dstleafID", UNKNOWN), lambda pkt:pkt.type == DP_TYPE)
                 ]

# Bind encapsulated layers together by a given value, otherwise Scapy doesn't know what is encaped
bind_layers(Ether, MTP, type=0x4133)
bind_layers(MTP, IP, type=9)
bind_layers(UDP, TEST, dport=28)