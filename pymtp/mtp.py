'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 04/28/2021
Desc: The protocol header for the Meshed Tree Protocol (MTP), which is the control-plane protocol which
      builds meshed trees on a network.
'''

from scapy.packet import bind_layers, Packet # Importing the super-class of all Scapy protocol headers
from scapy.layers.l2 import Ether # Importing the Ethernet II header for binding to the MTP header
from scapy.fields import (      # Importing a couple of pre-made field types
    ByteField,
    ByteEnumField,
    ShortField,
    StrLenField,
    FieldLenField
)

# Constants for MTP header information to give more context to default field parameters
UNKNOWN   = 0
ANCMT_TYPE = 1 # Annoucement message header type value
DP_TYPE = 9 # Data plane header type value

# MTP control plane header types
MTP_CP_Types = {
    0: "Unknown",
    1: "Announcement"
}

# MTP data plane header types
MTP_DP_Types = {
    0: "Unknown",
    9: "routed"
}


class MTP_Routed(Packet):
    name = "Meshed Tree Protocol (data plane)"

    # The fields that make up the protocol header
    fields_desc= [ 
                    ByteEnumField("type", DP_TYPE, MTP_DP_Types),
                    ShortField("srcleafID", UNKNOWN),
                    ShortField("dstleafID", UNKNOWN)
                 ]

    def extract_padding(self, s): # Not sure if I even need this
        return '', s


class MTP(Packet):
    name = "Meshed Tree Protocol (control plane)" # The name of the protocol

    # The fields that make up the protocol header
    fields_desc= [ 
                    ByteEnumField("type", UNKNOWN, MTP_CP_Types),
                    ShortField("leafID", UNKNOWN),
                    ShortField("spineID", UNKNOWN)
                 ]

bind_layers(Ether, MTP, type=0x4133)
bind_layers(MTP, MTP_Path, type=ADVT_TYPE)
bind_layers(MTP_Path, MTP_Path)