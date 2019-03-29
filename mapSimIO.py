import sys
from abc import ABC, abstractmethod
import csv
import re
import argparse
import xml.etree.ElementTree as ET

class Options:



    def __init__(self):
        
        self.projFile = ""
        self.plcName = ""
 

        
def main():

    # process command line
    parser = argparse.ArgumentParser()
    parser.add_argument("projFile", help="twincat tsproj xml input file")
    parser.add_argument("plcName",
                        help="twincat name of plc e.g. 'TIPC^XtesSxrPlc^XtesSxrPlc Instance'")
#    parser.add_argument("--plc", help="generate plc artifacts only", action="store_true")
#    parser.add_argument("--deviceFile", help="file containing devices to generate")
    args = parser.parse_args()

    options = Options()

    # make sure devInfo input file is specified
    if not args.projFile:
        sys.exit("no input project file specified")
    else:
        print()
        print("using project file: %s" % args.projFile)
        options.projFile = args.projFile

    # make sure plcName is specified
    if not args.plcName:
        sys.exit("no plcName specified")
    else:
        print()
        print("using plcName: %s" % args.plcName)
        options.plcName = args.plcName

    # parse xml project file
    try:
        tree = ET.parse(options.projFile)
    except Exception as ex:
        sys.exit("exception parsing project file: " + ex)

    # find the plc variable mappings
    root = tree.getroot()
    plcMap = root.findall("./Mappings/OwnerA[@Name='%s']" % options.plcName)
    if len(plcMap) != 1:
        sys.exit("found %d matches in project file for plc: %s" %
                 (len(plcMap), options.plcName))
    plcMap = plcMap[0]
    
    for deviceMap in plcMap.findall("OwnerB"):
        deviceName = deviceMap.attrib['Name']
        print()
        print("mappings for device: %s" % deviceName)
        for varLink in deviceMap.findall("Link"):
            print("\tfrom: %s" % varLink.attrib['VarA'])
            print("\t\tto: %s" % varLink.attrib['VarB'])

            # map deviceName and plc variable (VarA)
            # to sim variable and device name
            # VarB value should be same for both plc mapping and sim mapping



if __name__ == '__main__':
    main()
