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
        self.simTaskPrefix = ""
        self.simDevicePrefix = ""
        self.variableMapFile = ""
        self.signalMapFile = ""
 

        
def main():

    # process command line
    parser = argparse.ArgumentParser()
    parser.add_argument("projFile", help="twincat tsproj xml input file")
    parser.add_argument("plcName",
                        help="twincat name of plc e.g. 'TIPC^XtesSxrPlc^XtesSxrPlc Instance'")
    parser.add_argument("simTaskPrefix",
                        help="twincat task name for sim e.g. 'SimTask'")
    parser.add_argument("simDevicePrefix",
                        help="twincat device prefix for sim e.g. 'TIID^Device 2 (EtherCAT Simulation)^'")
    parser.add_argument("variableMapFile",
                        help="csv file from generator with plc variable, data type, and sim variable")
    parser.add_argument("signalMapFile",
                        help="csv file with plc data type, plc signal name, and sim signal name")
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

    # make sure simTaskPrefix is specified
    if not args.simTaskPrefix:
        sys.exit("no simTaskPrefix specified")
    else:
        print()
        print("using simTaskPrefix: %s" % args.simTaskPrefix)
        options.simTaskPrefix = args.simTaskPrefix

    # make sure simDevicePrefix is specified
    if not args.simDevicePrefix:
        sys.exit("no simDevicePrefix specified")
    else:
        print()
        print("using simDevicePrefix: %s" % args.simDevicePrefix)
        options.simDevicePrefix = args.simDevicePrefix

    # make sure variableMapFile is specified
    if not args.variableMapFile:
        sys.exit("no variableMapFile specified")
    else:
        print()
        print("using variableMapFile: %s" % args.variableMapFile)
        options.variableMapFile = args.variableMapFile

    # make sure signalMapFile is specified
    if not args.signalMapFile:
        sys.exit("no signalMapFile specified")
    else:
        print()
        print("using signalMapFile: %s" % args.signalMapFile)
        options.signalMapFile = args.signalMapFile

    # read variable map
    variableMap = {}
    try:
        with open(options.variableMapFile, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                plcVarName = row[0]
                variableData = {}
                variableData['type'] = row[1]
                variableData['simVar'] = row[2]
                variableMap[plcVarName] = variableData
            print("variable map file contains %d variable(s)" % (len(variableMap)))
    except Exception as ex:
        sys.exit("error opening variable map file: %s" % ex)

    # read signal map
    signalMap = {}
    try:
        with open(options.signalMapFile, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                plcType = row[0]
                if plcType not in signalMap:
                    signalMap[plcType] = {}
                signalData = signalMap[plcType]
                signalData[row[1]] = row[2]
            print("signal map file contains %d" % (len(signalMap)))
    except Exception as ex:
        sys.exit("error opening signal map file: %s" % ex)

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
        
        ind = deviceName.rfind('^')
        if ind == -1:
            sys.exit("unexpected device name format: %s" % deviceName)
        deviceName = deviceName[ind+1:]
        
        #print("mappings for device: %s" % deviceName)
        simDeviceName = options.simDevicePrefix + deviceName
        print("mapping to sim device: %s" % simDeviceName)
        
        for varLink in deviceMap.findall("Link"):
            plcVar = varLink.attrib['VarA']
            ioLink = varLink.attrib['VarB']
            print()
            print("\tVarA plc: %s" % plcVar)
            #print("\t\tto: %s" % ioLink)

            # strip off prefix
            ind = plcVar.find('^')
            if ind == -1:
                sys.exit("unexpected plc variable format: %s" % plcVar)
            plcVar = plcVar[ind+1:]

            # get plc var name tokens (doc name, variable name, and usually signal name)
            varTokens = plcVar.split('.')
            if len(varTokens) == 3:
                docName = varTokens[0]
                varName = varTokens[1]
                sigName = varTokens[2]
            elif len(varTokens) == 2:
                docName = varTokens[0]
                varName = varTokens[1]
            else:
                sys.exit("unexpected plc variable format: %s" % plcVar)


            #print("%s %s %s" % (docName, varName, sigName))
            
            # get plc data type and sim variable for plc variable
            if not varName in variableMap:
                sys.exit("no variable mapping found for %s" % varName)
                
            variableData = variableMap[varName]
            plcType = variableData['type']
            simVar = variableData['simVar']

            # get sim signal name for plc signal name
            
            if not plcType in signalMap:
                sys.exit("no type mapping found for type: %s" % (plcType))

            signalData = signalMap[plcType]
            if sigName not in signalData:
                sys.exit("no signal mapping found for signal: %s" % sigName)

            plcSignal = signalData[sigName]

            varASim = docName + "." + simVar + "." + plcSignal



            # TODO: need to prefix VarASim with simTaskPrefix + "Inputs" or "Outputs"


                  

            print("\tVarA sim: %s" % varASim)
            print("\tVarB: %s" % ioLink)

if __name__ == '__main__':
    main()
