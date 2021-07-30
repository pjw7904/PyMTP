'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 07/15/2021
Desc: Misc utility functions that gather information about the local box's network configuration.
'''
from socket import if_nameindex # socket stuff
from scapy.all import get_if_hwaddr, get_if_list


def getLocalInterfaces():
    loopbackIntName = 'lo' # Ubuntu/Linux(?) loopback interface name 
    intToSkip = "eth0"

    interfaceList = if_nameindex() # List which includes interfaces in tuples of format (int#, intName)
    filteredIntList = [int[1] for int in interfaceList if int[1] != intToSkip and int[1] != loopbackIntName] # Filter out the int# and any ints to skip over
    
    return filteredIntList


def getLocalMACAddressesFilter():
    macToSkip = "00:00:00:00:00:00"

    MACAddrs = [get_if_hwaddr(i) for i in get_if_list() if get_if_hwaddr(i) != macToSkip]

    filter = ""

    for mac in MACAddrs:
        filter += " not ether src host {0} and".format(mac)

    filter = filter.rstrip("and").strip()

    print("MAC filter:", filter)

    return filter