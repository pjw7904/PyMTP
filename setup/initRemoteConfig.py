'''
Author: Peter Willis (pjw7904@rit.edu)
Last Updated: 08/27/2021
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
    testSource = getConfigInfo("MTP Utilities", "localTestDirectory")
    codeDestination = getConfigInfo("GENI Credentials", "remoteCodeDirectory")

    # Grabbing configuration info from command-line arguments
    argParser = argparse.ArgumentParser(description = "PyMTP GENI Configuration")
    argParser.add_argument('--code', action = "store_true") # Upload main code directory (../pymtp)
    argParser.add_argument('--config', action = "store_true") # Configure GENI node with necessary software/libraries/packages
    argParser.add_argument('--test', action = "store_true") # Upload the test directory (../test)
    args = argParser.parse_args()

    # Config command to start a GNU screen and run through (MAKE SURE FILE IS LF NOT CRLF) 
    startConfig = "screen -dmS conf bash -c 'sudo bash pymtp/initfrr.sh; exec bash'"

    print("\n+---------Number of Nodes: {0}--------+".format(len(GENIDict)))
    print("NOTE: If you have previously configured this topology (--config)"
          " and included --config again, run \"sudo pkill screen\" using GENICmdExec.py")

    for node in GENIDict:
        print(node)

        if(args.code):
            uploadToGENINode(node, GENIDict, codeSource, codeDestination)
            print("\tPyMTP directory uploaded")

        if(args.test):
            uploadToGENINode(node, GENIDict, testSource, codeDestination)
            print("\ttest directory uploaded")

        if(args.config):
            orchestrateRemoteCommands(node, GENIDict, startConfig, waitForResult=False)
            print("\tInitial configuration script started")

if __name__ == "__main__":
    main() # run main