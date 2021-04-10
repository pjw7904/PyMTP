'''
Author: Peter Willis (pjw7904@rit.edu)

Desc: The protocol header for the Meshed Tree Protocol (MTP), which is the control-plane protocol which
      builds meshed trees on a network.
'''

from scapy.packet import Packet # Importing the super-class of all Scapy protocol headers
from scapy.fields import (      # Importing a couple of pre-made field types
    ByteField,
    ByteEnumField,
    ShortField,
    StrField,
    StrLenField,
)