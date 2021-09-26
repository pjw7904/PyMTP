import sys
sys.path.append("../pymtp")

from PIDTable import PIDTable
from NetUtils import getLocalInterfaces

test = PIDTable(getLocalInterfaces())
# adding compute subnets
test.addComputeSubnet("10.10.5.15", "255.255.255.0", "ethernet_0")
test.addComputeSubnet("15.22.10.254", "255.255.255.0", "ethernet_1")
test.addParent(15, [1,2,3], 55, "ethernet_2")
test.addChild(15, [1,2,3], "ethernet_3")
test.addChild(15, 1, "ethernet_4")
print(test.getTables())