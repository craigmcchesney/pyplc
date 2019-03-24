import sys
from abc import ABC, abstractmethod
import csv
import re
import argparse

class DeviceInfo:
    def __init__(self, name, tag, depGauge1, depGauge2, depPump1, depValve1, volume, depVol1, depVol2):
        self.name = name
        self.tag = tag
        self.depGauge1 = depGauge1
        self.depGauge2 = depGauge2
        self.depPump1 = depPump1
        self.depValve1 = depValve1
        self.volume = volume
        self.depVol1 = depVol1
        self.depVol2 = depVol2

        

# registers device class types with PlcDevice class for look up by tag
def register(deviceClass):
    PlcDevice.register(deviceClass.tag(), deviceClass)
    
# abstract base class for plc devices
class PlcDevice(ABC):



    deviceTypes = {}



    # register PlcDevice concrete classes for look up by tag
    @classmethod
    def register(cls, tag, theClass):
        cls.deviceTypes[tag] = theClass
        

    # return the class for the specified tag
    @classmethod
    def deviceType(cls, tag):
        return cls.deviceTypes[tag]
    


    # create instance of class with specified tag
    @classmethod
    def createDevice(cls, tag, deviceInfo):
        deviceClass = cls.deviceType(tag)
        deviceInstance = deviceClass(deviceInfo)
        return deviceInstance


    
    @staticmethod
    @abstractmethod # must be innermost decorator!
    def tag():
        pass



    def __init__(self, deviceInfo):
        self.deviceInfo = deviceInfo



    def name(self):
        return self.deviceInfo.name



    def volume(self):
        return self.deviceInfo.volume



    # return function block for plc code
    def plcFunctionBlock(self):
#        return VgcValveFB(self.deviceInfo)
        className = self.plcFunctionBlockType()
        cls = globals()[className]
        return cls(self.deviceInfo)



    @abstractmethod
    def plcFunctionBlockType(self):
        pass



class ValveDevice(PlcDevice):
    pass



class GaugeDevice(PlcDevice):
    pass



class PumpDevice(PlcDevice):
    pass



@register
class VgcValveDevice(ValveDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "VGC";



    def plcFunctionBlockType(self):
        return "VgcValveFB"



class ColdCathodeGaugeDevice(GaugeDevice):
    pass



@register
class Mks500GaugeDevice(ColdCathodeGaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS500";



    def plcFunctionBlockType(self):
        return "Mks500GaugeFB"



@register
class Mks500EPGaugeDevice(ColdCathodeGaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS500_EP";



    def plcFunctionBlockType(self):
        return "Mks500EPGaugeFB"



@register
class Mks275GaugeDevice(GaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS275";



    def plcFunctionBlockType(self):
        return "Mks275GaugeFB"



@register
class PipGammaPumpDevice(PumpDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "PIP_GAMMA";



    def plcFunctionBlockType(self):
        return "PipGammaPumpFB"



# abstract base class for plc code objects
class PlcObject(ABC):


    
    @abstractmethod
    def declaration(self):
        pass


    
    @abstractmethod
    def code(self):
        pass



    @abstractmethod
    def objectName(self):
        pass



    def pragma(self):
        return "{attribute 'pytmc' := ' pv: " + self.objectName() + " '}"

    

# abstract base class for function blocks
class PlcFunctionBlock(PlcObject):

    prefixFb = "fb_"

    def __init__(self, deviceInfo):
        self.fbName = self.prefixFb + deviceInfo.name.replace("-", "_")


    @abstractmethod
    def fbType(self):
        pass



    def objectName(self):
        return self.fbName


    
    def declaration(self):
        return self.fbName + " : " + self.fbType() + PlcGenerator.terminator



class ValveFB(PlcFunctionBlock):
    pass



class GaugeFB(PlcFunctionBlock):
    pass



class PumpFB(PlcFunctionBlock):
    pass



class VgcValveFB(ValveFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.upstreamGauge = deviceInfo.depGauge1
        self.downstreamGauge = deviceInfo.depGauge2



    def code(self):
        upGauge = PlcContainer.getFB(self.upstreamGauge)
        downGauge = PlcContainer.getFB(self.downstreamGauge)
        if ((not upGauge) or (not downGauge)):
            sys.exit("unable to find upGauge: %s or downGauge: %s" % (self.upstreamGauge, self.downstreamGauge))
        return (self.fbName +
                PlcGenerator.openParen +
                "i_stUSG := " +
                upGauge.fbName + ".IG" +
                ", i_stDSG := " +
                downGauge.fbName + ".IG" +
                ", i_xDis_DPIlk := FALSE, i_xEPS_OK := TRUE, i_xPMPS_OK := TRUE," +
                " i_xExt_OK := TRUE, i_xOverrideMode := xSystemOverrideMode" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

    def fbType(self):
        return "FB_VGC";



class ColdCathodeGaugeFB(GaugeFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.ionGauge = deviceInfo.depGauge1



    def code(self):
        ionGauge = PlcContainer.getFB(self.ionGauge)
        if ((not ionGauge)):
            sys.exit("unable to find ion gauge: %s" % self.ionGauge)
        return (self.fbName +
                PlcGenerator.openParen +
                "PG := " +
                ionGauge.fbName + ".PG" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    
class Mks500GaugeFB(ColdCathodeGaugeFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def fbType(self):
        return "FB_MKS500";



class Mks500EPGaugeFB(ColdCathodeGaugeFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def fbType(self):
        return "FB_MKS500_EP";



class Mks275GaugeFB(GaugeFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                "PG=>" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def fbType(self):
        return "FB_MKS275";



class PipGammaPumpFB(PumpFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.ccGauge = deviceInfo.depGauge1



    def code(self):
        ccGauge = PlcContainer.getFB(self.ccGauge)
        if ((not ccGauge)):
            # TODO: exit if dependencies don't exist?
            sys.exit("unable to find cold cathode gauge: %s" % self.ccGauge)
        return (self.fbName +
                PlcGenerator.openParen +
                "i_stGauge := " +
                ccGauge.fbName + ".PG" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def fbType(self):
        return "FB_PIP_GAMMA";



class DeviceContainer:



    deviceList = [] # list of device names as encountered in input for sequential access
    deviceMap = {} # map of device name to device object for indexed access



    @classmethod
    def addDevice(cls, deviceName, device):
        # device name must be unique
        if (deviceName in cls.deviceList):
            sys.exit("duplicate device name: " + deviceName)
        cls.deviceList.append(deviceName)
        cls.deviceMap[deviceName] = device


    
class PlcDocument:


    
    def __init__(self, docName):
        #super().__init__(docName)
        self.name = docName
        self.contentMap = {} # map of object type string keys to list of lines values



    def addContent(self, otype, lines):
        if (not otype in self.contentMap):
            self.contentMap[otype] = []
        self.contentMap[otype].extend(lines)



    def writeToFile(self, fobj, devOrdering):
        
        specifiedKeys = [s["type"] for s in devOrdering]
        unspecifiedKeys = [value for value in self.contentMap.keys() if value not in specifiedKeys]
        for k in unspecifiedKeys:
            devOrdering.append({"type":k, "label":k})
            
        for orderSpec in devOrdering:
            fbtype = orderSpec["type"]
            if (fbtype in self.contentMap.keys()):
                fobj.write("\n")
                fobj.write("// " + orderSpec["label"])
                fobj.write("\n\n")
                for fbd in self.contentMap[fbtype]:
                    fobj.write(fbd)
                    fobj.write("\n")                



class VariableDocument(PlcDocument):
    pass
                



class ProgramDocument(PlcDocument):
    pass


    
class PlcContainer:


    
    # maps with document name key to document object value
    varDocs = {}
    progDocs = {}
    
    # key is device name, value is map of plc object type to plc object instance
    # e.g., "TV3K0-VGC-1" -> {"fb" -> (instance of VgcValveFB))
    # for device dependency lookup
    plcDeviceMap = {}

    otypeFB = "fb"

    

    @classmethod
    def addToVariablesDocument(cls, docName, otype, lines):
        if (not docName in cls.varDocs):
            cls.varDocs[docName] = VariableDocument(docName)
        document = cls.varDocs[docName]
        document.addContent(otype, lines)



    @classmethod
    def addToProgramDocument(cls, docName, otype, lines):
        if (not docName in cls.progDocs):
            cls.progDocs[docName] = ProgramDocument(docName)
        document = cls.progDocs[docName]
        document.addContent(otype, lines)



    @classmethod
    def hasFB(cls, deviceName):
        return ((deviceName in cls.plcDeviceMap) and
                (cls.otypeFB in cls.plcDeviceMap[deviceName]))



    @classmethod
    def addFB(cls, deviceName, fbObj):
        if not deviceName in cls.plcDeviceMap:
            cls.plcDeviceMap[deviceName] = {}
        else:
            # device shouldn't already be in map
            sys.exit("%s already in plcDeviceMap" % (deviceName))
        if cls.otypeFB in cls.plcDeviceMap[deviceName]:
            # shouldn't already be a function block in the map for this device
            sys.exit("function block for %s already in plcDeviceMap" % (deviceName))
        else:          
            devObjMap = cls.plcDeviceMap[deviceName]
            devObjMap[cls.otypeFB] = fbObj
            return True



    @classmethod
    def getFB(cls, deviceName):
        if ((not deviceName in cls.plcDeviceMap) or
            (not cls.otypeFB in cls.plcDeviceMap[deviceName])):
            return None
        else:
            devObjMap = cls.plcDeviceMap[deviceName]
            return devObjMap[cls.otypeFB]



class PlcGenerator:

    openParen = "("
    closeParen = ")"
    terminator = ";"



    @classmethod
    def generate(cls):

        cls.generatePlc()
        cls.generateSim()


        
    @classmethod
    def generatePlc(cls):

        # iterate through devices and create plc objects organized into files
        for devName in DeviceContainer.deviceList:
            device = DeviceContainer.deviceMap[devName]
            docName = device.volume()

            plcFB = PlcContainer.getFB(devName)
            
            decs = []
            decs.append(plcFB.pragma())
            decs.append(plcFB.declaration())
            PlcContainer.addToVariablesDocument(docName, plcFB.fbType(), decs)

            code = []
            code.append(plcFB.code())
            PlcContainer.addToProgramDocument(docName, plcFB.fbType(), code)

        # set up ordering of devices by type
        deviceOrdering = []
        deviceOrdering.append({"type":"FB_MKS275", "label":"MKS275 Gauges"})
        deviceOrdering.append({"type":"FB_MKS500", "label":"MKS500 Gauges"})
        deviceOrdering.append({"type":"FB_MKS500_EP", "label":"MKS500_EP Gauges"})
        deviceOrdering.append({"type":"FB_VGC", "label":"VGC Valves"})
        deviceOrdering.append({"type":"FB_PIP_GAMMA", "label":"PIP_Gamma Pumps"})
        
        # write variables documents
        for docName, document in PlcContainer.varDocs.items():
            with open('gen.plc.GVL_' + docName.upper(), 'w') as f:
                document.writeToFile(f, deviceOrdering)

        # write program documents
        for docName, document in PlcContainer.progDocs.items():
            with open('gen.plc.PRG_' + docName.upper(), 'w') as f:
                document.writeToFile(f, deviceOrdering)

                
    @classmethod
    def generateSim(cls):
        pass


    
class DeviceHandler:



    volumes = []
    devices = []
    deviceTypes = set()


    
    @classmethod
    def handleDevice(cls, rowCount, info):
        
        iName = info["Device Name"]
        iTag = info["PLC Tag"].upper()
        iDepGauge1 = info["PLC dep gauge1"]
        iDepGauge2 = info["PLC dep gauge2"]
        iDepPump1 = info["PLC dep pump1"]
        iDepValve1 = info["PLC dep valve1"]
        iVolume = info["Volume"]
        iDepVol1 = info["sim dep vol1"]
        iDepVol2 = info["sim dep vol2"]

        # if we have a non-empty device list, only create the devices it contains
        if (((not len(cls.devices)) and (not len(cls.volumes))) or
            ((len(cls.devices)) and (iName in cls.devices)) or
            ((len(cls.volumes)) and (iVolume in cls.volumes))):

            if ((not iName) or (len(iName) == 0)):
                sys.exit("no iName provided for row %d: %s" % (rowCount, info))

            if ((not iTag) or (len(iTag) == 0)):
                sys.exit("missing plc tag for row %d: %s" % (rowCount, info))

            if ((not iVolume) or (len(iVolume) == 0)):
                sys.exit("missing volume for row %d: %s" % (rowCount, info))

            cls.deviceTypes.add(iTag)

            devInfo = DeviceInfo(iName, iTag, iDepGauge1, iDepGauge2, iDepPump1,
                                 iDepValve1, iVolume, iDepVol1, iDepVol2)
            
            device = PlcDevice.createDevice(iTag, devInfo)
            
            if (not device):
                sys.exit("no device created for row %d: %s" % (rowCount, info))
            else:
                DeviceContainer.addDevice(iName, device)
                plcFB = device.plcFunctionBlock()
                PlcContainer.addFB(iName, plcFB)
           

        


    @classmethod
    def printReport(cls):
        print("==================================================")
        print("SUMMARY")
        print("==================================================")
        print("devices created: %d" % len(DeviceContainer.deviceList))

        # print file with all unique devices
        try:
            with open('gen.plc.deviceTypes', 'w') as f:
                for dtype in sorted(cls.deviceTypes):
                    f.write(dtype)
                    f.write("\n")
        except Exception as ex:
            print(ex)
            sys.exit("failed to create ./plc.deviceTypes file")
        


def main():

    # process command line
    parser = argparse.ArgumentParser()
    parser.add_argument("deviceInfoFile", help="csv file with device info, expected format is first line with column names %s" % ("Device Name, PLC Tag, PLC dep gauge1, PLC dep gauge2, PLC dep pump1, PLC dep valve1, Volume, sim dep vol1, sim dep vol2"))
    parser.add_argument("--tags", help="list unique tag types for specified devices", action="store_true")
    parser.add_argument("--deviceFile", help="file containing devices to generate")
    parser.add_argument("--volumeFile", help="file containing volumes to generate")
    args = parser.parse_args()

    # make sure devInfo input file is specified
    if not args.deviceInfoFile:
        sys.exit("no device info file specified")
    else:
        print("using device info file: %s" % args.deviceInfoFile)

    # read optional list of volumes to create
    volFile = args.volumeFile
    if volFile:
        print("generating volumes containined in file: %s" % volFile)
        try:
            with open(volFile, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    DeviceHandler.volumes.append(row[0])
                print("creating %d volume(s) in volumes list: %s" % (len(DeviceHandler.volumes), DeviceHandler.volumes))
        except Exception as ex:
            print(ex)

    # read optional list of devices to create
    devFile = args.deviceFile
    if devFile:
        print("generating devices containined in file: %s" % devFile)
        try:
            with open(devFile, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    DeviceHandler.devices.append(row[0])
                print("creating %d devices in device list: %s" % (len(DeviceHandler.devices), DeviceHandler.devices))
        except Exception as ex:
            print(ex)

        listTagsOnly = False
        if args.tags:
            listTagsOnly = True
            print("printing unique tags for specified devices")
            sys.exit("printing tags not yet implemented")

    with open('./device-info.csv', newline='') as f:

        rowCount = 0
        reader = csv.DictReader(f)

        for row in reader:
            rowCount = rowCount + 1
            DeviceHandler.handleDevice(rowCount, row)

        PlcGenerator.generate()
        DeviceHandler.printReport()



if __name__ == '__main__':
    main()
