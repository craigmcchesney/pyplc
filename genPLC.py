import sys
import csv
import re
from abc import ABC, abstractmethod


class DeviceInfo:
    def __init__(self, name, tag, depGauge1, depGauge2, depPump1, depValve1):
        self.name = name
        self.tag = tag
        self.depGauge1 = depGauge1
        self.depGauge2 = depGauge2
        self.depPump1 = depPump1
        self.depValve1 = depValve1

        

# abstract base class for plc objects
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
                ", i_xDis_DPIlk := TRUE, i_xEPS_OK := TRUE, i_xPMPS_OK := TRUE," +
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
        # TODO: log errors
        if not deviceName in cls.plcDeviceMap:
            cls.plcDeviceMap[deviceName] = {}
        else:
            # device shouldn't already be in map
            return False
        if cls.otypeFB in cls.plcDeviceMap[deviceName]:
            # shouldn't already be a function block in the map for this device
            return False
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


    
class DeviceFactory:

    @classmethod
    def createDevice(cls, deviceInfo):

        if PlcContainer.hasFB(deviceInfo.name):
            # already exists so fail
            # TODO: exit here?
            return None

        fb = None
        
        # valves

        # VGC valve
        if (deviceInfo.tag == "VGC"):
            fb = VgcValveFB(deviceInfo)
 
        # gauges

        # MKS500 gauge
        elif (deviceInfo.tag == "MKS500"):
            fb = Mks500GaugeFB(deviceInfo)

        # MKS500_EP gauge
        elif (deviceInfo.tag == "MKS500_EP"):
            fb = Mks500EPGaugeFB(deviceInfo)

        # MKS275 gauge
        elif (deviceInfo.tag == "MKS275"):
            fb = Mks275GaugeFB(deviceInfo)

        # pumps

        # PIP_GAMMA pump
        elif (deviceInfo.tag == "PIP_Gamma"):
            fb = PipGammaPumpFB(deviceInfo)

        else:
            # unhandled device tag
            # TODO: exit here?
            return None

        success = PlcContainer.addFB(deviceInfo.name, fb)
        if success:
            return fb
        else:
            # TODO: handle failure, exit?
            return None




class DeviceHandler:



    devices = []
    nameWarnings = []
    mfrWarnings = []
    deviceWarnings = []
    deviceCount = 0


    
    @classmethod
    def handleDevice(cls, rowCount, info):
        
        iName = info[3]
        iTag = info[5]
        iDepGauge1 = info[6]
        iDepGauge2 = info[7]
        iDepPump1 = info[8]
        iDepValve1 = info[9]

        if ((not iName) or (len(iName) == 0)):
            cls.nameWarnings.append(
                "no iName provided for row %d: %s" % (rowCount, info))
            return
        
        if ((not iTag) or (len(iTag) == 0)):
            cls.mfrWarnings.append(
                "missing plc tag for row %d: %s" % (rowCount, info))
            return
        
        devInfo = DeviceInfo(iName, iTag, iDepGauge1, iDepGauge2, iDepPump1, iDepValve1)

        # if we have a non-empty device list, only create the devices it contains
        if ((not len(cls.devices)) or ((len(cls.devices)) and (iName in cls.devices))):
            device = DeviceFactory.createDevice(devInfo)
            if (not device):
                cls.deviceWarnings.append(
                    "no device created for row %d: %s" % (rowCount, info))
            else:
                cls.deviceCount = cls.deviceCount + 1
        


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
        print("devices created: %d" % cls.deviceCount)
        print("\tfunction blocks: %d" % len(PlcContainer.FBs))
        print("create failures: %d" % len(cls.deviceWarnings))
        


def main():

    # read optional list of devices to create, otherwise try to create everything
    try:
        with open('./device-list.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                DeviceHandler.devices.append(row[0])
            print("creating %d devices in device list: %s" % (len(DeviceHandler.devices), DeviceHandler.devices))
    except:
        pass

    with open('./device-info.csv', newline='') as f:

        rowCount = 0
        reader = csv.reader(f)

        for row in reader:

            rowCount = rowCount + 1

            # skip header
            if (rowCount < 4):
                continue

            DeviceHandler.handleDevice(rowCount, row)

        print(PlcContainer.plcDeviceMap)

        PlcGenerator.generate()

        DeviceHandler.printReport()



if __name__ == '__main__':
    main()
