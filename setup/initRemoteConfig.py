'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 05/18/2021
Desc: Automated configuration of remote nodes on GENI that are a part of a PyMTP topology/experiment.
      Please update your GENI configuration file if you haven't done so.
'''

from GENIutils import uploadToGENINode, getConfigInfo, buildDictonary, orchestrateRemoteCommands
import argparse # for command-line input

def main():
    # Grabbing configuration info from GENI config file
    rspec = getConfigInfo("Local Utilities", "RSPEC")
    GENIDict = buildDictonary(rspec)
    codeSource = getConfigInfo("MTP Utilities", "localCodeDirectory")
    codeDestination = getConfigInfo("GENI Credentials", "remoteCodeDirectory")

    # Grabbing configuration info from command-line arguments
    argParser = argparse.ArgumentParser(description = "PyMTP GENI Configuration")
    argParser.add_argument('--code', action = "store_true") # Upload main code directory (../pymtp)
    argParser.add_argument('--config', action = "store_true") # Configure GENI node with necessary software/libraries/packages
    args = argParser.parse_args()

    # Config command to start a GNU screen and run through 
    startConfig = "screen -dmS conf bash -c 'sudo bash pymtp/initCmds.sh; exec bash'"

    print("\n+---------Number of Nodes: {0}--------+".format(len(GENIDict)))
    for node in GENIDict:
        if(args.code):
            uploadToGENINode(node, GENIDict, codeSource, codeDestination)
        if(args.config):
            orchestrateRemoteCommands(node, GENIDict, startConfig, waitForResult=False)

if __name__ == "__main__":
    main() # run main