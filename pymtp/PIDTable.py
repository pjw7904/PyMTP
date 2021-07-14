'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 07/13/2021
Desc: Class to define the structure, logic, and behaviors of an MTP Path Identifier (PID) table.
      For both leaves and spines.
'''
from collections import namedtuple

# Table entry format for tier 1 nodes (leaves)
EdgeEntry = namedtuple("Edge_Entry", "IPv4NetworkID IPv4NetworkMask DestLeafID EgressInt")

# Table entry format for tier 2+ nodes (spines)
CoreEntry = namedtuple("Core_Entry", "LeafID Cost IngressInt")

# Table entry format for all nodes which connect to a higher tier
UpstreamEntry = namedtuple("Upstream_Entry", "PID EgressPort LastTimestamp")

class PIDTable:
    # Constructor, initalize the table itself (a list)
    def __init__(self):
        # The tables are lists (for now at least)
        self.table = []
        self.upstreamTable = []

    def addParent(self):
        return

    def addChild(self):
        return