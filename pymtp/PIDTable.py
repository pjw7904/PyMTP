'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 07/28/2021
Desc: Class to define the structure, logic, and behaviors of an MTP Path Identifier (PID) table.
      For both leaves and spines.
'''
from collections import namedtuple
from datetime import datetime
from ipaddress import IPv4Address

# Table entry format for tier 1 nodes (leaves)
EdgeEntry = namedtuple("Edge_Entry", "IPv4NetworkID IPv4NetworkMask DestLeafID EgressInt")

# Table entry format for tier 2+ nodes (spines)
CoreEntry = namedtuple("Core_Entry", "leafID spineID Cost intf")

# Table entry format for all nodes which connect to a higher tier
UpstreamEntry = namedtuple("Upstream_Entry", "PID EgressPort LastTimestamp")

class PIDTable:
    # Constructor, initalize the table itself (a list)
    def __init__(self, numOfInts):
        # The tables are lists (for now at least)
        self.table = []
        self.upstreamTable = []
        self.numInts = numOfInts

    def addParent(self, leafID, spineID, cost, port):
        newEntry = CoreEntry(leafID, spineID, cost, port)
        self.table.append(newEntry)
        return

    def addChild(self, PID, port):
        currentTime = datetime.now().time()
        newEntry = UpstreamEntry(PID, port, currentTime)
        self.upstreamTable.append(newEntry)
        return

    def getEgressLeafPort(self, dstLeafID):
        for entry in self.table:
            if dstLeafID == entry.leafID:
                return entry.intf
        return "None"

    def getEgressSpinePort(self, srcIPv4, dstIPv4):
        key = "{srcIP};{dstIP}".format(srcIP=srcIPv4, dstIP=dstIPv4)

        IPHash = hash(key)
        egressPortNum = (IPHash % self.numInts) + 1 # +1 to get x in ethx and offset the 0 it starts at
        egressPortName = "eth{0}".format(egressPortNum)

        return egressPortName

    def getTables(self):
        print("====Main Table====")
        for entry in self.table:
            print(entry)
        print("==================")

        print("====Upstream Table====")
        for entry in self.upstreamTable:
            print(entry)
        print("======================")       
        return