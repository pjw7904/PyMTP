'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 09/26/2021
Desc: Class to define the structure, logic, and behaviors of an MTP Path Identifier (PID) table.
      For both leaves and spines.
'''
from collections import namedtuple
from datetime import datetime
from NetUtils import getIPv4NetworkID
import logging

# Table entry format for a node which is a compute node attached to this node
EdgeEntry = namedtuple("Edge_Entry", "IPv4Network")

# Table entry format for a node which is a parent of this node
DownstreamEntry = namedtuple("Downstream_Entry", "leafID spineID Cost LastTimestamp")

# Table entry format for a node which is a child of this node
UpstreamEntry = namedtuple("Upstream_Entry", "leafID PID EgressPort LastTimestamp")

# Table entry format for an interface that hasn't been modified yet
DefaultEntry = namedtuple("Default_Entry", "leafID defaultValue")

class PIDTable:
    # Constructor, initalize the table itself (a dictionary)
    def __init__(self, intfList):
        self.table = {}
        self.intfDict = {}
        self.nonComputeIntfs = []
        self.portKey = 0

        for intf in intfList:
            self.table[intf] = DefaultEntry(-1, "unused")
            self.nonComputeIntfs.append(intf)

    def addComputeSubnet(self, IPv4Address, IPv4Mask, intf):
        try:
            self.table[intf] = EdgeEntry(getIPv4NetworkID(IPv4Address, IPv4Mask))
            self.nonComputeIntfs.remove(intf)
        except ValueError:
            print("{0} {1} is not a valid IPv4 network, rejecting entry".format(IPv4Address, IPv4Mask))
            self.table[intf] = DefaultEntry(-1, "unused")

        return

    # Adds a parent for the node, which is closer to the compute nodes/subnets (leaf parent for a spine)
    def addParent(self, leafID, spineID, cost, intf):
        if type(self.table[intf]) is not list: # We need to convert the structure to a list. Perhaps because it was an upstream interface prior?
            self.table[intf] = []
        self.table[intf].append(DownstreamEntry(leafID, spineID, cost, datetime.now().time()))

        return

    # Adds a child for the node, which is deeper/higher into the Folded-Clos topology (spine child for a leaf)
    def addChild(self, leafID, spineID, intf):
        if type(spineID) is list:
            spineID = '.'.join(map(str, spineID))

        PID = "{LID}.{SID}".format(LID=leafID, SID=spineID)

        self.table[intf] = UpstreamEntry(leafID, PID, intf, datetime.now().time())
        self.intfDict[self.portKey] = intf
        self.portKey += 1
        
        return

    #BUG: You never know about other pod's leaf IDs, you just know about your own, so upstream ones will keep going until you hit the top, which will know if its correct or not
    def getEgressInterface(self, srcLeafID, dstLeafID):
        egressIntf = self.getEgressDownstreamInterface(dstLeafID)

        if(egressIntf == "None"):
            egressIntf = self.getEgressUpstreamInterface(srcLeafID, dstLeafID)
            
        return egressIntf

    # Determines which interface/leaf node to send a packet to, utilizes MTP routed header information
    def getEgressDownstreamInterface(self, dstLeafID):
        for intf in self.table:
            if isinstance(self.table[intf], list):
                for leafIDEntry in self.table[intf]:
                    if isinstance(leafIDEntry, DownstreamEntry) and dstLeafID == leafIDEntry.leafID:
                        logging.debug("\n[routing] Msg routed DOWN towards destination")
                        return intf

        return "None"

    # Determines which interface/spine node to send a packet to via L3 addressing or MTP ID addressing, utilizes common hashing techniques
    def getEgressUpstreamInterface(self, srcID, dstID):
        logging.debug("\n[routing] Msg attempted to be routed UP")

        # Craft a string-based key in the form: "sourceIdentifier;destinationIdentifier"
        key = "{src};{dst}".format(src=srcID, dst=dstID)

        # Input key into the hashing algorithm and get egress interface (uses built-in Python 3 hashing algorithm, whatever it may be)
        IPHash = hash(key)

        try:
            egressIntfNum = (IPHash % self.portKey) # To get X in ethX
        except ZeroDivisionError:
            return "None"

        egressIntfName = self.intfDict[egressIntfNum]

        return egressIntfName
    
    def getChildPID(self, intf):
        return self.table[intf].PID

    def getNonComputeInterfaces(self):
        return self.nonComputeIntfs

    # Prints table entries
    def getTables(self):
        tableOutput = ""

        tableOutput += "\n====MTP Table====\n"
        for entry in self.table:
            tableOutput += "{intf} - {entryInfo}\n".format(intf=entry, entryInfo=self.table[entry])
        tableOutput += "==================\n"
    
        return tableOutput