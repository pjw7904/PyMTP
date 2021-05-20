'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 05/18/2021
Desc: Automated configuration of remote nodes on GENI that are a part of a PyMTP topology/experiment.
      Please update your GENI configuration file if you haven't done so.
'''

from GENIutils import getConfigInfo, buildDictonary, orchestrateRemoteCommands
import argparse # for command-line input

def main():
    # Grabbing configuration info from GENI config file
    rspec = getConfigInfo("Local Utilities", "RSPEC")
    GENIDict = buildDictonary(rspec)
    codeSource = getConfigInfo("MTP Utilities", "localCodeDirectory")
    codeDestination = getConfigInfo("GENI Credentials", "remoteCodeDirectory")

    notDone = True
    allCmds = []

    while notDone:
        cmd = input("Enter a valid bash command: ")
        if cmd != "done":
            allCmds.append(cmd)
        else:
            notDone = False

    print("\n+---------Number of Nodes: {0}--------+".format(len(GENIDict)))
    for node in GENIDict:
        orchestrateRemoteCommands(node, GENIDict, allCmds)

if __name__ == "__main__":
    main() # run main