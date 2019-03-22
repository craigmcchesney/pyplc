import sys
import csv
import re
from abc import ABC, abstractmethod


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
    @abstractmethod
    def plcFunctionBlock(self):
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



    def plcFunctionBlock(self):
        return VgcValveFB(self.deviceInfo)



class ColdCathodeGaugeDevice(GaugeDevice):
    pass



@register
class Mks500GaugeDevice(ColdCathodeGaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS500";



    def plcFunctionBlock(self):
        return Mks500GaugeFB(self.deviceInfo)



@register
class Mks500EPGaugeDevice(ColdCathodeGaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS500_EP";



    def plcFunctionBlock(self):
        return Mks500EPGaugeFB(self.deviceInfo)



@register
class Mks275GaugeDevice(GaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS275";



    def plcFunctionBlock(self):
        return Mks275GaugeFB(self.deviceInfo)



@register
class PipGammaPumpDevice(PumpDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "PIP_GAMMA";



    def plcFunctionBlock(self):
        return PipGammaPumpFB(self.deviceInfo)



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
            # TODO: exit if dependencies don't exist?
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
            # TODO: exit if dependencies don't exist?
            sys.exit("unable to find ion gague: %s" % self.ionGauge)
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


    
class PlcContainer:


    
    # core data structure
    # key is device name, value is map of plc object type to plc object instance
    # e.g., "TV3K0-VGC-1" -> {"fb" -> (instance of VgcValveFB))
    plcDeviceMap = {}

    # need ordered list of function blocks for generation, points to same fb object as plcDeviceMap
    FBs = []

    otypeFB = "fb"


    
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
            cls.FBs.append(fbObj)
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

    fbDeclarations = {}
    fbCode = {}
    openParen = "("
    closeParen = ")"
    terminator = ";"



    @classmethod
    def addFbDeclaration(cls, fbType, fbDeclaration):
        if fbType not in cls.fbDeclarations:
            cls.fbDeclarations[fbType] = []
        fbDecls = cls.fbDeclarations[fbType]
        fbDecls.append(fbDeclaration)


        
    @classmethod
    def addFbCode(cls, fbType, fbCode):
        if fbType not in cls.fbCode:
            cls.fbCode[fbType] = []
        code = cls.fbCode[fbType]
        code.append(fbCode)


        
    @classmethod
    def generate(cls):

        cls.generatePlc()
        cls.generateSim()


        
    @classmethod
    def generatePlc(cls):

        # iterate through devices and create plc objects organized into files
        for devName in DeviceContainer.deviceList:
            device = DeviceContainer.deviceMap[devName]
            devFile = device.volume()
            plcFB = device.plcFunctionBlock()
            PlcContainer.addFB(device.name(), plcFB)

        # add declarations and program code for function blocks
        for fb in PlcContainer.FBs:

            # organize declarations and code by object type for readability
            fbType = fb.fbType()

            # function block variable declaration
            cls.addFbDeclaration(fbType, fb.pragma())
            cls.addFbDeclaration(fbType, fb.declaration())

            # function block invocation program code
            cls.addFbCode(fbType, fb.code())

        # set up ordering of devices by type
        deviceOrdering = []
        deviceOrdering.append({"type":"FB_MKS275", "label":"MKS275 Gauges"})
        deviceOrdering.append({"type":"FB_MKS500", "label":"MKS500 Gauges"})
        deviceOrdering.append({"type":"FB_MKS500_EP", "label":"MKS500_EP Gauges"})
        deviceOrdering.append({"type":"FB_VGC", "label":"VGC Valves"})
        deviceOrdering.append({"type":"FB_PIP_GAMMA", "label":"PIP_Gamma Pumps"})
        
        # write declarations file
        with open('plc.GVL_DEVICES', 'w') as f:
            for orderSpec in deviceOrdering:
                fbtype = orderSpec["type"]
                if (fbtype in cls.fbDeclarations):
                    f.write("\n")
                    f.write("// " + orderSpec["label"])
                    f.write("\n\n")
                    for fbd in cls.fbDeclarations[fbtype]:
                        f.write(fbd)
                        f.write("\n")

        # write program file
        with open('plc.PRG_PLC', 'w') as f:
            for orderSpec in deviceOrdering:
                fbtype = orderSpec["type"]
                if (fbtype in cls.fbCode):
                    f.write("\n")
                    f.write("// " + orderSpec["label"])
                    f.write("\n\n")
                    for s in cls.fbCode[fbtype]:
                        f.write(s)
                        f.write("\n")
        

                
    @classmethod
    def generateSim(cls):
        pass


    
class DeviceHandler:



    devices = []
    deviceTypes = set()
    nameWarnings = []
    mfrWarnings = []
    deviceWarnings = []


    
    @classmethod
    def handleDevice(cls, rowCount, info):
        
        iName = info[2]
        iTag = info[4].upper()
        iDepGauge1 = info[5]
        iDepGauge2 = info[6]
        iDepPump1 = info[7]
        iDepValve1 = info[8]
        iVolume = info[9]
        iDepVol1 = info[10]
        iDepVol2 = info[11]

        cls.deviceTypes.add(iTag)

        # if we have a non-empty device list, only create the devices it contains
        if ((not len(cls.devices)) or ((len(cls.devices)) and (iName in cls.devices))):

            if ((not iName) or (len(iName) == 0)):
                sys.exit("no iName provided for row %d: %s" % (rowCount, info))

            if ((not iTag) or (len(iTag) == 0)):
                sys.exit("missing plc tag for row %d: %s" % (rowCount, info))

            if ((not iVolume) or (len(iVolume) == 0)):
                sys.exit("missing plc tag for row %d: %s" % (rowCount, info))

            devInfo = DeviceInfo(iName, iTag, iDepGauge1, iDepGauge2, iDepPump1,
                                 iDepValve1, iVolume, iDepVol1, iDepVol2)
            
            device = PlcDevice.createDevice(iTag, devInfo)
            
            if (not device):
                sys.exit("no device created for row %d: %s" % (rowCount, info))
            else:
                DeviceContainer.addDevice(iName, device)
        


    @classmethod
    def printReport(cls):
        # print()
        # print("==================================================")
        # print("NAME WARNINGS")
        # print("==================================================")
        # for w in cls.nameWarnings:
        #     print(w)
        # print()
        # print("==================================================")
        # print("MFR WARNINGS")
        # print("==================================================")
        # for w in cls.mfrWarnings:
        #     print(w)
        # print()
        print("==================================================")
        print("SUMMARY")
        print("==================================================")
        print("devices created: %d" % len(DeviceContainer.deviceList))
        print("\tfunction blocks: %d" % len(PlcContainer.FBs))
        print("create failures: %d" % len(cls.deviceWarnings))

        # print file with all unique devices
        try:
            with open('plc.deviceTypes', 'w') as f:
                for dtype in sorted(cls.deviceTypes):
                    f.write(dtype)
                    f.write("\n")
        except Exception as ex:
            print(ex)
            sys.exit("failed to create ./plc.deviceTypes file")
        


def main():

    # read optional list of devices to create, otherwise try to create everything
    try:
        with open('./device-list.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                DeviceHandler.devices.append(row[0])
            print("creating %d devices in device list: %s" % (len(DeviceHandler.devices), DeviceHandler.devices))
    except Exception as ex:
        print(ex)
        sys.exit("error processing device-list file")

    with open('./device-info.csv', newline='') as f:

        rowCount = 0
        reader = csv.reader(f)

        for row in reader:

            rowCount = rowCount + 1

            # skip header
            if (rowCount < 6):
                continue

            DeviceHandler.handleDevice(rowCount, row)

        PlcGenerator.generate()

        DeviceHandler.printReport()



if __name__ == '__main__':
    main()
