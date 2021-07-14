import sys
sys.path.append("../pymtp")

from PIDTable import PIDTable
from time import sleep

test = PIDTable()

test.addChild("120.1", "eth1")
test.addChild("120.2", "eth2")
test.addChild("120.3", "eth3")
test.addChild("120.4", "eth4")

test.addParent("120", 1, "eth1")
test.addParent("130", 1, "eth2")
test.addParent("140", 1, "eth3")
test.addParent("150", 1, "eth4")

test.getTables()