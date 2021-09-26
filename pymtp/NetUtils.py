'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 08/09/2021
Desc: Misc utility functions that gather information about the local box's network configuration.
'''
from socket import if_nameindex # socket stuff
from scapy.all import get_if_hwaddr, get_if_list
from netifaces import ifaddresses, AF_INET, AF_LINK
from ipaddress import ip_network

# Gets the names of local interfaces (ex: eth1)
def getLocalInterfaces():
    loopbackIntName = 'lo' # Ubuntu/Linux(?) loopback interface name 
    intToSkip = "eth0"

    interfaceList = if_nameindex() # List which includes interfaces in tuples of format (int#, intName)
    filteredIntList = [int[1] for int in interfaceList if int[1] != intToSkip and int[1] != loopbackIntName] # Filter out the int# and any ints to skip over
    
    return filteredIntList

# Get an IPv4 address from an interface name
def getIPv4Address(intf):
    return ifaddresses(intf)[AF_INET][0]['addr']
    
# Get an IPv4 subnet mask from an interface name
def getIPv4NetMask(intf):
    return ifaddresses(intf)[AF_INET][0]['netmask']

# Get the Network ID for a given network
def getIPv4NetworkID(ipv4Addr, ipv4Mask):
    ipv4Info = "{addr}/{mask}".format(addr=ipv4Addr,mask=ipv4Mask)
    return ip_network(ipv4Info, strict=False)

# Get a MAC address from an interface name
def getMACAddress(intf):
    return ifaddresses(intf)[AF_LINK][0]['addr']

# Crafts the appropriate Berkley Packet Filter (BPF) string for Scapy sniffing on an MTP switch (currently not used)
def getLocalMACAddressesFilter():
    macToSkip = "00:00:00:00:00:00"

    MACAddrs = [get_if_hwaddr(i) for i in get_if_list() if get_if_hwaddr(i) != macToSkip]

    filter = ""

    for mac in MACAddrs:
        filter += " not ether src host {0} and".format(mac)

    filter = filter.rstrip("and").strip()

    return filter