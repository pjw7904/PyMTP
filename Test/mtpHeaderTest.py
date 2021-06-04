import sys
sys.path.append("../pymtp")

from scapy.all import * # import all of the default scapy library
from mtp import MTP, MTP_Path # import MTP headers

def main():
    path1 = MTP_Path(cost=5, path="12345")
    path2 = MTP_Path(cost=23, path="14654343")
    pathList = [path1, path2]

    testMTPFrame = MTP(type=3, operation=1, port=1, paths=pathList)

    ls(testMTPFrame)
    testMTPFrame.show()
    testMTPFrame.show2()

if __name__ == "__main__":
    main() # run main