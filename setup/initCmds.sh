sudo apt-get update
sudo apt-get -y install chrony python3-pip
sudo sed -i '/^$/d; /#/d; s/pool/#pool/g; $ a\\n#MTP/PyMTP Research Time Server Information (questions? pjw7904@rit.edu)\nserver time.google.com iburst' /etc/chrony/chrony.conf
sudo invoke-rc.d chrony restart && sudo chronyc -a 'burst 4/4' && sudo chronyc -a makestep
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install tshark
sudo python3 -m pip install scapy==2.4.4 configparser