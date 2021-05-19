'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 05/18/2021
Desc: Automated configuration of remote nodes on GENI that are a part of a PyMTP topology/experiment.
      Please update your GENI configuration file if you haven't done so.
'''

from GENIutils import uploadToGENINode, getConfigInfo, buildDictonary, orchestrateRemoteCommands

def main():
    # Grabbing configuration info from GENI config file
    rspec = getConfigInfo("Local Utilities", "RSPEC")
    GENIDict = buildDictonary(rspec)
    codeSource = getConfigInfo("MTP Utilities", "localCodeDirectory")
    codeDestination = getConfigInfo("GENI Credentials", "remoteCodeDirectory")

    startConfig = "screen -dmS conf bash -c 'sudo bash pymtp/initCmds.sh; exec bash'"
    #stopConfig = "sudo pkill screen"

    print("\n+---------Number of Nodes: {0}--------+".format(len(GENIDict)))
    for node in GENIDict:
        uploadToGENINode(node, GENIDict, codeSource, codeDestination)
        orchestrateRemoteCommands(node, GENIDict, startConfig)

if __name__ == "__main__":
    main() # run main