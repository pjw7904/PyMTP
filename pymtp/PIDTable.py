'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 09/21/2021
Desc: Class to define the structure, logic, and behaviors of an MTP Path Identifier (PID) table.
      For both leaves and spines.
'''
from collections import namedtuple
from datetime import datetime

# Table entry format for tier 1 nodes (leaves)
EdgeEntry = namedtuple("Edge_Entry", "IPv4NetworkID IPv4NetworkMask DestLeafID EgressInt")

# Table entry format for tier 2+ nodes (spines)
CoreEntry = namedtuple("Core_Entry", "leafID spineID Cost intf")

# Table entry format for all nodes which connect to a higher tier
UpstreamEntry = namedtuple("Upstream_Entry", "PID EgressPort LastTimestamp")

class PIDTable:
    # Constructor, initalize the table itself (a list)
    def __init__(self):
        self.table = []
        self.upstreamTable = []
        self.intfDict = {}
        self.portKey = 0

    # Adds a parent for the node, which is closer to the compute nodes/subnets (leaf parent for a spine)
    def addParent(self, leafID, spineID, cost, port):
        newEntry = CoreEntry(leafID, spineID, cost, port)
        self.table.append(newEntry)
        return

    # Adds a child for the node, which is deeper/higher into the Folded-Clos topology (spine child for a leaf)
    def addChild(self, PID, port):
        currentTime = datetime.now().time()
        newEntry = UpstreamEntry(PID, port, currentTime)
        self.upstreamTable.append(newEntry)
        self.intfDict[self.portKey] = port
        self.portKey += 1
        return

    # Determines which interface/leaf node to send a packet to, utilizes MTP routed header information
    def getEgressLeafPort(self, dstLeafID):
        for entry in self.table:
            if dstLeafID == entry.leafID:
                return entry.intf
        return "None"

    # Determines which interface/spine node to send a packe to, utilizes common hashing techniques
    def getEgressSpinePort(self, srcIPv4, dstIPv4):
        # Craft a string-based key in the form: "sourceIPv4Address;destinationIPv4Address"
        key = "{srcIP};{dstIP}".format(srcIP=srcIPv4, dstIP=dstIPv4)

        # Input key into the hashing algorithm and get egress interface (uses built-in Python 3 hashing algorithm, whatever it may be)
        IPHash = hash(key)
        egressPortNum = (IPHash % self.portKey) # To get X in ethX
        egressPortName = self.intfDict[egressPortNum]

        return egressPortName

    # Prints table entries
    def getTables(self):
        tableOutput = ""

        tableOutput += "\n====Main Table====\n"
        for entry in self.table:
            tableOutput += str(entry) + "\n"
        tableOutput += "==================\n"

        tableOutput += "====Upstream Table====\n"
        for entry in self.upstreamTable:
            tableOutput += str(entry) + "\n"
        tableOutput += "======================\n" 
    
        return tableOutput