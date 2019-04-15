import sys
from abc import ABC, abstractmethod
import csv
import re
import argparse
import xml.etree.ElementTree as ET
import pickle

class Options:



    def __init__(self):
        
        self.projFile = ""
        self.plcName = ""
        self.simName = ""
        self.simTaskPrefix = ""
        self.simDevicePrefix = ""
        self.variableMapFile = ""
 

        
def indent(elem, level=0):
    # borrowed from http://effbot.org/zone/element-lib.htm#prettyprint
    
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i



def main():

    # process command line
    parser = argparse.ArgumentParser()
    parser.add_argument("projFile", help="twincat tsproj xml input file")
    parser.add_argument("plcName",
                        help="twincat name of plc e.g. 'TIPC^XtesSxrPlc^XtesSxrPlc Instance'")
    parser.add_argument("simName",
                        help="twincat name of sim plc e.g. 'TIPC^ProtoSimPLC^ProtoSimPLC Instance'")
    parser.add_argument("simTaskPrefix",
                        help="twincat task name for sim e.g. 'SimTask'")
    parser.add_argument("simDevicePrefix",
                        help="twincat device prefix for sim e.g. 'TIID^Device 2 (EtherCAT Simulation)^'")
    parser.add_argument("variableMapFile",
                        help="csv file from generator with plc variable, data type, and sim variable")
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

    # make sure simName is specified
    if not args.simName:
        sys.exit("no simName specified")
    else:
        print()
        print("using simName: %s" % args.simName)
        options.simName = args.simName

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

    # read variable map
    variableMap = {}
    try:
        with open(options.variableMapFile, 'rb') as f:
            variableMap = pickle.load(f)
            print("variable map file contains %d variable(s)" % (len(variableMap)))
    except Exception as ex:
        sys.exit("error opening variable map file: %s" % ex)

    signalMap = {
        "FB_VGC" : {
            "q_xOPN_DO" : "i_xSol",
            "i_xOpnLS" : "q_xOpnLS",
            "i_xClsLS" : "q_xClsLS"},
        "FB_MKS500" : {
            "i_iPRESS_R" : "q_iRawPress",
            "i_xHV_ON" : "q_xHVOn",
            "i_xDisc_Active" : "q_DisActive",
            "q_xHV_DIS" : "i_xHvOn"},
        "FB_MKS275" : {
            "i_iPRESS_R" : "q_iRawPress"},
        "FB_PIP_Gamma" : {
            "q_xHVEna_DO" : "xOn",
            "i_xSP_DI" : "?unmapped"}}

    # parse xml project file
    try:
        tree = ET.parse(options.projFile)
    except Exception as ex:
        sys.exit("exception parsing project file: " + ex)

    root = tree.getroot()
    mappingRoot = root.find("./Mappings")
    if not mappingRoot:
        sys.exit("project file doesn't contain a 'Mappings' section")

    # find the plc variable mappings
    plcMap = root.findall("./Mappings/OwnerA[@Name='%s']" % options.plcName)
    if len(plcMap) != 1:
        sys.exit("found %d matches in project file for plc: %s" %
                 (len(plcMap), options.plcName))
    plcMap = plcMap[0]

    # exit if there are already sim variable mappings,
    #otherwise create a new section for the mappings
    simMap = root.findall("./Mappings/OwnerA[@Name='%s']" % options.simName)
    if len(simMap) != 0:
        sys.exit("found existing variable mappings for sim: %s" %
                 (options.simName))
    else:
        simMap = ET.SubElement(mappingRoot, 'OwnerA')
        simMap.set("Name", options.simName)
    
    for deviceMap in plcMap.findall("OwnerB"):
        
        deviceName = deviceMap.attrib['Name']
        print()
        
        ind = deviceName.rfind('^')
        if ind == -1:
            sys.exit("unexpected device name format: %s" % deviceName)
        deviceName = deviceName[ind+1:]

        # create name for io device node and add it to the simMap container
        simDeviceName = options.simDevicePrefix + deviceName
        deviceNode = ET.SubElement(simMap, 'OwnerB')
        deviceNode.set("Name", simDeviceName)

        for varLink in deviceMap.findall("Link"):
            plcVar = varLink.attrib['VarA']
            ioLink = varLink.attrib['VarB']

            # strip off task name / and "Inputs" or "Outputs", but first use to determine
            # whether to link to the sim's inputs or output (opposite of the plc value)
            ind = plcVar.find('^')
            if ind == -1:
                sys.exit("unexpected plc variable format: %s" % plcVar)
            inoutSpec = plcVar[0:ind]
            if "Inputs" in inoutSpec:
                inoutSpec = "Outputs"
            elif "Outputs" in inoutSpec:
                inoutSpec = "Inputs"
            else:
                sys.exit("unexpected plc task prefix format: %s" % inoutSpec)
            plcVar = plcVar[ind+1:]

            # create sim task prefix with "Inputs" or "Outputs" appended as appropriate
            simTaskInoutPrefix = options.simTaskPrefix + " " + inoutSpec

            # get plc var name tokens (doc name, variable name, and usually signal name)
            varTokens = plcVar.split('.')
            if len(varTokens) == 3:
                docName = varTokens[0]
                varName = varTokens[1]
                sigName = varTokens[2]
            else:
                sys.exit("unexpected plc variable format: %s" % plcVar)

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
                sys.exit("no signal mapping found for type: %s signal: %s" % (plcType, sigName))
            simSignal = signalData[sigName]
            if simSignal == "?unmapped": # don't map this signal to the sim
                continue

            varASim = simTaskInoutPrefix + "^" + docName + "." + simVar + "." + simSignal

            linkNode = ET.SubElement(deviceNode, 'Link')
            linkNode.set("VarA", varASim)
            linkNode.set("VarB", ioLink)

    ET.dump(simMap)
    indent(root)
    tree.write(options.projFile)

if __name__ == '__main__':
    main()
