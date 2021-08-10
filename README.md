# PyMTP

OVERVIEW:
A simple, Python-based, software switch that runs the Meshed Tree Protocol (MTP) as its Layer 2 control-plane protocol and standard 802.1D bridging for data-plane forwarding

This switch is meant to easily display the functionality of MTP and to rapidly prototype modifications to the MTP standard.

The MTP-based switch can either be run independently on its own machine (using physical devices or a testbed like GENI) or via Mininet using the provided Mininet switch extension.

NOTE: 
	I use the "python3" command for all scripts here, which is how it has to be used on the GENI nodes. 
	Your local system might be just "python" when running the scripts, but it has to be Python 3. Same goes for sudo.

DIRECTORY BREAKDOWN:
	pymtp/ - MTP switch code and any utility files/functions that are used in the switch code. This directory is uploaded to GENI nodes.
	setup/ - Scripts to set up the remote GENI topology and associated files to configure everything.
	test/  - Small test scripts I have build as I am working on the main code. You can ignore this.

STEPS TO GET THE TOPOLOGY SET UP:
1. create a 2-tier Folded-Clos topology on GENI, where all leaf nodes are connected to all spine nodes and there is a compute node connected to each leaf node.

2. Inside of the setup folder, update creds.cnf with your information. You can ignore the test folder. The pymtp folder is where the actual MTP switch code is
	located.

3. Inside of the setup folder, run the following:
		python3 initRemoteConfig.py --code --config
	This will upload the pymtp folder to each GENI node and create a screen session (in the background) to start installing necessary packages.
	It will not alert you when it is done, and all nodes will perform these installations at the same time, so I would leave it for 30 minutes and
	come back. If a package cannot be found later, it might be because it hasn't fully installed everything or an installation failed.
	This process also turns off IPv4 routing on every GENI node.

RUNNING/TESTING PYMTP:
1. It is best to test this with two leafs, its two compute nodes, and then all of the spines. I would open a shell for each of the mentioned devices

2. Currently, leaf nodes will not accept compute node/client traffic until it has heard from all of the connected spines, so spine nodes have to be
	started first. On each spine node in the topology, run the following:
		cd pymtp/
		sudo python3 MTP_switch.py
	it will just sit there waiting for a leaf to connect to it, so it will purposefully hang. Once a new leaf node has contacted it, updated table information
	will be printed.
	
3. After all of the spines have been started, now the leaf nodes have to be started with the following commands:
		cd pymtp/
		sudo python3 MTP_switch.py --leaf [eth interface where the client is]
			example: sudo python3 MTP_switch.py --leaf eth3
	you should see some table information printed for each spine it has connected to. You know it is ready for client/compute node traffic when it prints
	"looking for client traffic"
	
4. Test traffic forwarding and look at the output for leaves and spines by sending a simple ping from one compute node/client to the other. I limit it to
	four echo pings so that the output doesn't get clogged up:
		ping [eth1 IPv4 address of destination client] -c 4
	these pings should SUCCEED when the MTP switches are up and running, and FAIL when they are all turned off. An updated traffic generator will
	come later. For now, simple back-and-forth communication is proven to work via a ping test.