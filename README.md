# PyMTP

## OVERVIEW
A simple, Python-based, software switch that runs the Meshed Tree Protocol (MTP) as its Layer 2 control-plane protocol and standard 802.1D bridging for data-plane forwarding

This switch is meant to easily display the functionality of MTP and to rapidly prototype modifications to the MTP standard.

The MTP-based switch can either be run independently on its own machine (using physical devices or a testbed like GENI) or via Mininet using the provided Mininet switch extension.

**NOTE:** 
I use the "python3" command for all scripts here, but your local python 3 installation might use the command "python" instead. Regardless, it has to be Python 3. Same goes for the sudo command.

## DIRECTORY BREAKDOWN
* pymtp/ - MTP switch code and any utility files/functions that are used in the switch code. This directory is uploaded to GENI nodes.
* setup/ - Scripts to set up the remote GENI topology and associated files to configure everything.
* test/  - Small test scripts I have build as I am working on the main code. You can ignore this.

## STEPS TO GET THE TOPOLOGY SET UP
1. Create a valid n-tier folded-Clos topology on [GENI](https://www.geni.net)

2. Inside of the setup directory, update creds.cnf with your information.

3. Inside of the setup directory, run the following: `python3 initRemoteConfig.py --code --config`

This will upload the pymtp folder to each GENI node and create a screen session (in the background) to start installing necessary packages.
It will not alert you when it is done, and all nodes will perform these installations at the same time, so I would leave it for 30 minutes and
come back. If a package cannot be found later, it might be because it hasn't fully installed everything or an installation failed.
This process also turns off IPv4 routing on every GENI node.

## RUNNING/TESTING PYMTP
**NOTE:** Any PyMTP startup command can remove the `--log DEBUG` argument if you don't want as verbose of an output.

1. Log into the GENI nodes via SSH. You should be in your home folder (/users/you) and see the pymtp directory. Stay in this home directory.

2. Start up the top tier of spine nodes first with the command: `sudo python3 pymtp --log DEBUG --top`

3. Start up the other tiers of spine nodes next with the command: `sudo python3 pymtp --log DEBUG`

4. Determine the compute subnet interface (ethx) on each leaf node and then start them with the command: `sudo python3 pymtp --leaf [ethx] --log DEBUG`

5. On any two compute nodes on different leaves, ping to the destination IPv4 address, it should work.