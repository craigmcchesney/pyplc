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
        className = self.plcFunctionBlockType()
        cls = globals()[className]
        return cls(self.deviceInfo)



    @abstractmethod
    def plcFunctionBlockType(self):
        pass



    # return function block for sim code
    def simFunctionBlock(self):
        className = self.simFunctionBlockType()
        cls = globals()[className]
        return cls(self.deviceInfo)



    @abstractmethod
    def simFunctionBlockType(self):
        pass



    # return struct for sim code
    def simStruct(self):
        className = self.simStructType()
        cls = globals()[className]
        return cls(self.deviceInfo)



    @abstractmethod
    def simStructType(self):
        pass



class ValveDevice(PlcDevice):
    pass



class GaugeDevice(PlcDevice):
    pass



class PumpDevice(PlcDevice):
    pass



@register
class VcnValveDevice(ValveDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "VCN";



    def plcFunctionBlockType(self):
        return "VcnValveFB"



    def simFunctionBlockType(self):
        return "SimVacuumValveFB"



    def simStructType(self):
        return "SimVacuumValveStruct"



@register
class VgcValveDevice(ValveDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "VGC";



    def plcFunctionBlockType(self):
        return "VgcValveFB"



    def simFunctionBlockType(self):
        return "SimVacuumValveFB"



    def simStructType(self):
        return "SimVacuumValveStruct"



@register
class VrcValveDevice(ValveDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "VRC";



    def plcFunctionBlockType(self):
        return "VrcValveFB"



    def simFunctionBlockType(self):
        return "SimVacuumValveFB"



    def simStructType(self):
        return "SimVacuumValveStruct"



class ColdCathodeGaugeDevice(GaugeDevice):
    pass



@register
class Mks422GaugeDevice(ColdCathodeGaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS422";



    def plcFunctionBlockType(self):
        return "Mks422GaugeFB"



    def simFunctionBlockType(self):
        return "SimMks422GaugeFB"



    def simStructType(self):
        return "SimMks422GaugeStruct"



@register
class Mks500GaugeDevice(ColdCathodeGaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS500";



    def plcFunctionBlockType(self):
        return "Mks500GaugeFB"



    def simFunctionBlockType(self):
        return "SimMks500GaugeFB"



    def simStructType(self):
        return "SimMks500GaugeStruct"



@register
class Mks500EPGaugeDevice(ColdCathodeGaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS500_EP";



    def plcFunctionBlockType(self):
        return "Mks500EPGaugeFB"



    def simFunctionBlockType(self):
        return "SimMks500GaugeFB"



    def simStructType(self):
        return "SimMks500GaugeStruct"



@register
class Mks275GaugeDevice(GaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS275";



    def plcFunctionBlockType(self):
        return "Mks275GaugeFB"



    def simFunctionBlockType(self):
        return "SimMks275GaugeFB"



    def simStructType(self):
        return "SimMks275GaugeStruct"



@register
class Mks317GaugeDevice(GaugeDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "MKS317";



    def plcFunctionBlockType(self):
        return "Mks317GaugeFB"



    # TODO: what is function block type for MKS_317?
    def simFunctionBlockType(self):
        pass
        #return "FB_MKS_275"



    def simStructType(self):
        return "SimMks317GaugeStruct"



@register
class PipGammaPumpDevice(PumpDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "PIP_GAMMA";



    def plcFunctionBlockType(self):
        return "PipGammaPumpFB"



    def simFunctionBlockType(self):
         return "SimGamPipPumpFB"



    def simStructType(self):
        return "SimGamPipPumpStruct"


    
@register
class PtmTwisTorrPumpFB(PumpDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "PTM_TWISTORR";



    def plcFunctionBlockType(self):
        return "PtmTwisTorrPumpFB"


    # TODO: sim function block type?
    def simFunctionBlockType(self):
        pass
         #return "FB_GAM_PIP"



    # TODO: sim struct type?
    def simStructType(self):
        pass
        #return "ST_GAM_PIP"


    
# abstract base class for plc code objects
class PlcObject(ABC):


    
    def __init__(self, deviceInfo):
        self.container = None


        
    @abstractmethod
    def declaration(self):
        pass


    
    def simpleDeclaration(self):
        return self.objectName() + " : " + self.oType() + PlcGenerator.terminator


    
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
    def oType(self):
        pass



    @abstractmethod
    def code(self):
        pass



    def objectName(self):
        return self.fbName


    
    def declaration(self):
        return self.simpleDeclaration()



class VcnValveFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)


    # TODO: what value for i_ReqPos
    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                "i_xExtIlkOK := TRUE, i_ReqPos := TODO" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

    def oType(self):
        return "FB_VCN";



class VgcValveFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.upstreamGauge = deviceInfo.depGauge1
        self.downstreamGauge = deviceInfo.depGauge2



    def code(self):
        upGauge = self.container.getFB(self.upstreamGauge)
        downGauge = self.container.getFB(self.downstreamGauge)
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

    

    def oType(self):
        return "FB_VGC";



class VrcValveFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def code(self):
        return (self.fbName +
                "i_xExtILK_OK := TRUE, i_xOverrideMode := xSystemOverrideMode" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

    def oType(self):
        return "FB_VRC";



class ColdCathodeGaugeFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.ionGauge = deviceInfo.depGauge1



    def code(self):
        ionGauge = self.container.getFB(self.ionGauge)
        if ((not ionGauge)):
            sys.exit("unable to find ion gauge: %s" % self.ionGauge)
        return (self.fbName +
                PlcGenerator.openParen +
                "PG := " +
                ionGauge.fbName + ".PG" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    
class Mks422GaugeFB(ColdCathodeGaugeFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "FB_MKS422";



class Mks500GaugeFB(ColdCathodeGaugeFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "FB_MKS500";



class Mks500EPGaugeFB(ColdCathodeGaugeFB):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "FB_MKS500_EP";



class Mks275GaugeFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                "PG=>" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def oType(self):
        return "FB_MKS275";



class Mks317GaugeFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                "PG=>" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def oType(self):
        return "FB_MKS317";



class PipGammaPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.ccGauge = deviceInfo.depGauge1



    def code(self):
        ccGauge = self.container.getFB(self.ccGauge)
        if ((not ccGauge)):
            # TODO: exit if dependencies don't exist?
            sys.exit("unable to find cold cathode gauge: %s" % self.ccGauge)
        return (self.fbName +
                PlcGenerator.openParen +
                "i_stGauge := " +
                ccGauge.fbName + ".PG" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def oType(self):
        return "FB_PIP_GAMMA";



class PtmTwisTorrPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                PlcGenerator.closeParen +
                "i_xExtILKOk := TRUE" +
                PlcGenerator.terminator)
    

    def oType(self):
        return "FB_PTM_TwisTorr";



class SimVacuumValveFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.upstreamVolume = deviceInfo.depVol1
        self.downstreamVolume = deviceInfo.depVol2
        self.valve = deviceInfo.name



    def code(self):
        upVol = self.container.getStruct(self.upstreamVolume)
        downVol = self.container.getStruct(self.downstreamVolume)
        valve = self.container.getStruct(self.valve)
        if ((not upVol) or (not downVol) or (not valve)):
            sys.exit("unable to find upVol: %s downVol: %s or valve: %s" %
                     (self.upstreamVolume, self.downstreamVolume, self.valve))
        return (self.fbName +
                PlcGenerator.openParen +
                "stAVol := " +
                upVol.structName +
                ", stBvol := " +
                downVol.structName +
                ", stValve := " +
                valve.structName +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

    def oType(self):
        return "FB_VacuumValve";



class SimGaugeFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.volume = deviceInfo.volume
        self.gauge = deviceInfo.name



    def code(self):
        volume = self.container.getStruct(self.volume)
        gauge = self.container.getStruct(self.gauge)
        if ((not volume) or (not gauge)):
            sys.exit("unable to find volume: %s or gauge: %s" % (self.volume, self.gauge))
        return (self.fbName +
                PlcGenerator.openParen +
                "stVolume := " +
                volume.structName +
                ", stGauge := " +
                gauge.structName +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

class SimMks422GaugeFB(SimGaugeFB):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "FB_MKS_422";




class SimMks500GaugeFB(SimGaugeFB):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "FB_MKS_500";




class SimMks275GaugeFB(SimGaugeFB):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "FB_MKS_275";




class SimMks317GaugeFB(SimGaugeFB):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        pass
        #return "FB_MKS_317";




class SimGamPipPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.volume = deviceInfo.volume
        self.pip = deviceInfo.name



    def code(self):
        volume = self.container.getStruct(self.volume)
        pip = self.container.getStruct(self.pip)
        if ((not volume) or (not pip)):
            sys.exit("unable to find volume: %s or pip: %s" % (self.volume, self.pip))
        return (self.fbName +
                PlcGenerator.openParen +
                "stVolume := " +
                volume.structName +
                ", stPip := " +
                pip.structName +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

    def oType(self):
        return "FB_GAM_PIP";



# abstract base class for structs
class PlcStruct(PlcObject):

    prefixSt = "st_"

    def __init__(self, deviceInfo):
        self.structName = self.prefixSt + deviceInfo.name.replace("-", "_")


    def objectName(self):
        return self.structName



class SimVolumeStruct(PlcStruct):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def declaration(self):
        return (self.objectName() + " : " +
                self.oType() + " := " +
                PlcGenerator.openParen +
                "rVolume := 1E3, rPressure := Global_Pressure, rVLeak := Global_Leak" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)



    def oType(self):
        return "ST_Volume";



class SimVacuumValveStruct(PlcStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def declaration(self):
        return (self.objectName() + " : " +
                self.oType() + " := " +
                PlcGenerator.openParen +
                "q_xClsLS := TRUE, q_xOpnLS := FALSE" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)



    def oType(self):
        return "ST_VacuumValve";



class SimGaugeStruct(PlcStruct):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def declaration(self):
        return (self.objectName() + " : " +
                self.oType() + " := " +
                PlcGenerator.openParen +
                "q_xGaugeConnected := TRUE" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)



class SimMks422GaugeStruct(SimGaugeStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "ST_MKS_422";




class SimMks500GaugeStruct(SimGaugeStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "ST_MKS_500";




class SimMks317GaugeStruct(SimGaugeStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "ST_MKS_317";




class SimMks275GaugeStruct(SimGaugeStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def oType(self):
        return "ST_MKS_275";




class SimGamPipPumpStruct(PlcStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def declaration(self):
        return self.simpleDeclaration()

    

    def oType(self):
        return "ST_GAM_PIP";



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



    otypeFB = "fb"
    otypeStruct = "st"


    
    def __init__(self):
        
        # maps with document name key to document object value
        self.varDocs = {}
        self.progDocs = {}

        # key is device name, value is map of plc object type to plc object instance
        # e.g., "TV3K0-VGC-1" -> {"fb" -> (instance of VgcValveFB))
        # for device dependency lookup
        self.plcDeviceMap = {}

    

    def addToVariablesDocument(self, docName, otype, lines):
        if (not docName in self.varDocs):
            self.varDocs[docName] = VariableDocument(docName)
        document = self.varDocs[docName]
        document.addContent(otype, lines)



    def addToProgramDocument(self, docName, otype, lines):
        if (not docName in self.progDocs):
            self.progDocs[docName] = ProgramDocument(docName)
        document = self.progDocs[docName]
        document.addContent(otype, lines)



    def addPlcObj(self, deviceName, plcType, plcObj):
        
        if not deviceName in self.plcDeviceMap:
            self.plcDeviceMap[deviceName] = {}
            
        if plcType in self.plcDeviceMap[deviceName]:
            # shouldn't already be a plc object in the map of this type for this device
            sys.exit("function block for %s already in plcDeviceMap" % (deviceName))
        else:          
            devObjMap = self.plcDeviceMap[deviceName]
            devObjMap[plcType] = plcObj
            plcObj.container = self
            return True



    def hasPlcObj(self, deviceName, plcType):
        return ((deviceName in self.plcDeviceMap) and
                (plcType in self.plcDeviceMap[deviceName]))



    def getPlcObj(self, deviceName, plcType):
        if ((not deviceName in self.plcDeviceMap) or
            (not plcType in self.plcDeviceMap[deviceName])):
            return None
        else:
            devObjMap = self.plcDeviceMap[deviceName]
            return devObjMap[plcType]
        
    def hasFB(self, deviceName):
        return self.hasPlcObj(deviceName, self.otypeFB)



    def addFB(self, deviceName, fbObj):
        return self.addPlcObj(deviceName, self.otypeFB, fbObj)
        


    def getFB(self, deviceName):
        return self.getPlcObj(deviceName, self.otypeFB)



    def addStruct(self, deviceName, structObj):
        return self.addPlcObj(deviceName, self.otypeStruct, structObj)



    def hasStruct(self, deviceName):
        return self.hasPlcObj(deviceName, self.otypeStruct)



    def getStruct(self, deviceName):
        return self.getPlcObj(deviceName, self.otypeStruct)



class SimContainer(PlcContainer):


    
    def __init__(self):
        super().__init__()
        self.volumes = []



    def addVolume(self, volume):
        self.volumes.append(volume)



class PlcGenerator:


    
    openParen = "("
    closeParen = ")"
    terminator = ";"



    @classmethod
    def generatePlc(cls, container):

        # iterate through devices and create plc objects organized into files
        for devName in DeviceContainer.deviceList:
            device = DeviceContainer.deviceMap[devName]
            docName = device.volume()

            plcFB = container.getFB(devName)
            
            decs = []
            decs.append(plcFB.pragma())
            decs.append(plcFB.declaration())
            container.addToVariablesDocument(docName, plcFB.oType(), decs)

            code = []
            code.append(plcFB.code())
            container.addToProgramDocument(docName, plcFB.oType(), code)

        # set up ordering of devices by type
        deviceOrdering = []
        deviceOrdering.append({"type":"FB_MKS275", "label":"MKS275 Gauges"})
        deviceOrdering.append({"type":"FB_MKS500", "label":"MKS500 Gauges"})
        deviceOrdering.append({"type":"FB_MKS500_EP", "label":"MKS500_EP Gauges"})
        deviceOrdering.append({"type":"FB_VGC", "label":"VGC Valves"})
        deviceOrdering.append({"type":"FB_PIP_GAMMA", "label":"PIP_Gamma Pumps"})
        
        # write variables documents
        for docName, document in container.varDocs.items():
            with open('gen.plc.GVL_' + docName.upper(), 'w') as f:
                document.writeToFile(f, deviceOrdering)

        # write program documents
        for docName, document in container.progDocs.items():
            with open('gen.plc.PRG_' + docName.upper(), 'w') as f:
                document.writeToFile(f, deviceOrdering)

                
    @classmethod
    def generateSim(cls, container):

        # iterate through volumes and add declarations for volume structs
        for volName in container.volumes:
            
            volStruct = container.getStruct(volName)
            decs = []
            decs.append(volStruct.declaration())
            container.addToVariablesDocument(volName, volStruct.oType(), decs)

        # iterate through devices and create plc objects organized into files
        for devName in DeviceContainer.deviceList:
            
            device = DeviceContainer.deviceMap[devName]
            docName = device.volume()

            # add declarations for structs
            
            struct = container.getStruct(devName)

            decs = []
            decs.append(struct.declaration())
            container.addToVariablesDocument(docName, struct.oType(), decs)

            # add declarations and code for function blocks
            
            fb = container.getFB(devName)
            
            decs = []
            decs.append(fb.declaration())
            container.addToVariablesDocument(docName, fb.oType(), decs)

            code = []
            code.append(fb.code())
            container.addToProgramDocument(docName, fb.oType(), code)

        # # set up ordering of devices by type
        deviceOrdering = []
        # deviceOrdering.append({"type":"FB_MKS275", "label":"MKS275 Gauges"})
        # deviceOrdering.append({"type":"FB_MKS500", "label":"MKS500 Gauges"})
        # deviceOrdering.append({"type":"FB_MKS500_EP", "label":"MKS500_EP Gauges"})
        # deviceOrdering.append({"type":"FB_VGC", "label":"VGC Valves"})
        # deviceOrdering.append({"type":"FB_PIP_GAMMA", "label":"PIP_Gamma Pumps"})
        
        # write variables documents
        for docName, document in container.varDocs.items():
            with open('gen.sim.GVL_' + docName.upper(), 'w') as f:
                document.writeToFile(f, deviceOrdering)

        # write program documents
        for docName, document in container.progDocs.items():
            with open('gen.sim.PRG_' + docName.upper(), 'w') as f:
                document.writeToFile(f, deviceOrdering)

                
class DeviceHandler:



    volumes = []
    devices = []
    deviceTypes = set()


    
    @classmethod
    def handleDevice(cls, rowCount, info, plcContainer, simContainer, listTagsOnly=False):
        
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

            if listTagsOnly:
                cls.deviceTypes.add(iTag)

            else:

                devInfo = DeviceInfo(iName, iTag, iDepGauge1, iDepGauge2, iDepPump1,
                                     iDepValve1, iVolume, iDepVol1, iDepVol2)

                device = PlcDevice.createDevice(iTag, devInfo)

                if (not device):
                    sys.exit("no device created for row %d: %s" % (rowCount, info))
                else:

                    # store device
                    DeviceContainer.addDevice(iName, device)

                    # store plc objects
                    plcFB = device.plcFunctionBlock()
                    plcContainer.addFB(iName, plcFB)

                    # store sim objects

                    if not simContainer.hasStruct(device.volume()):
                        volumeInfo = DeviceInfo(device.volume(),
                                                "SIMVOLUME", "", "", "", "", device.volume(), "", "")
                        volumeStruct = SimVolumeStruct(volumeInfo)
                        simContainer.addStruct(device.volume(), volumeStruct)
                        simContainer.addVolume(device.volume())
                    
                    simStruct = device.simStruct()
                    simContainer.addStruct(iName, simStruct)
                    
                    simFB = device.simFunctionBlock()
                    simContainer.addFB(iName, simFB)
           

        


    @classmethod
    def printResult(cls, listTagsOnly=False):

        if listTagsOnly:
            
            # print all unique devices
            for dtype in sorted(cls.deviceTypes):
                print(dtype)

        else:
            print("==================================================")
            print("SUMMARY")
            print("==================================================")
            print("devices created: %d" % len(DeviceContainer.deviceList))
        


def main():

    # process command line
    parser = argparse.ArgumentParser()
    parser.add_argument("deviceInfoFile", help="csv file with device info, expected format is first " +
                        "line with column names %s" % ("Device Name, PLC Tag, PLC dep gauge1, " +
                                                       "PLC dep gauge2, PLC dep pump1, PLC dep valve1, " +
                                                       "Volume, sim dep vol1, sim dep vol2"))
    parser.add_argument("--tags", help="list unique tag types for specified devices", action="store_true")
    parser.add_argument("--deviceFile", help="file containing devices to generate")
    parser.add_argument("--volumeFile", help="file containing volumes to generate")
    args = parser.parse_args()

    # make sure devInfo input file is specified
    if not args.deviceInfoFile:
        sys.exit("no device info file specified")
    else:
        print()
        print("using device info file: %s" % args.deviceInfoFile)

    # read optional list of volumes to create
    volFile = args.volumeFile
    if volFile:
        print()
        print("using volumes file: %s" % volFile)
        try:
            with open(volFile, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    DeviceHandler.volumes.append(row[0])
                print("volumes file contains %d volume(s): %s" % (len(DeviceHandler.volumes),
                                                                  DeviceHandler.volumes))
        except Exception as ex:
            print(ex)

    # read optional list of devices to create
    devFile = args.deviceFile
    if devFile:
        print()
        print("using devices file: %s" % devFile)
        try:
            with open(devFile, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    DeviceHandler.devices.append(row[0])
                print("devices file contains %d device(s): %s" % (len(DeviceHandler.devices),
                                                                  DeviceHandler.devices))
        except Exception as ex:
            print(ex)

    # if this flag is specified, we only want to list the unique tag types, don't generate anything
    listTagsOnly = False
    if args.tags:
        listTagsOnly = True
        print()
        print("printing unique tags for specified devices")
        print()

    # create PLC and sim containers
    plcContainer = PlcContainer()
    simContainer = SimContainer()

    with open(args.deviceInfoFile, newline='') as f:

        rowCount = 0
        reader = csv.DictReader(f)

        # generate devices, plc objects, and sim objects
        for row in reader:
            rowCount = rowCount + 1
            DeviceHandler.handleDevice(rowCount, row, plcContainer, simContainer, listTagsOnly=listTagsOnly)

        # generate plc and sim code
        PlcGenerator.generatePlc(plcContainer)
        PlcGenerator.generateSim(simContainer)

        # print summary
        DeviceHandler.printResult(listTagsOnly=listTagsOnly)



if __name__ == '__main__':
    main()
