import sys
from abc import ABC, abstractmethod
import csv
import re
import argparse
import pickle

class DeviceInfo:
    
    def __init__(self, name, tag, depGauge1, depGauge2, depPump1, depValve1, volume, depVol1, depVol2, progUnit):
        
        self.name = name
        self.tag = tag
        self.depGauge1 = depGauge1
        self.depGauge2 = depGauge2
        self.depPump1 = depPump1
        self.depValve1 = depValve1
        self.volume = volume
        self.depVol1 = depVol1
        self.depVol2 = depVol2
        self.progUnit = progUnit

        

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
    


    # check if device is supported by generator
    @classmethod
    def isSupported(cls, tag):
        return tag in cls.deviceTypes


    
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



    def progUnit(self):
        return self.deviceInfo.progUnit



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



    def simFunctionBlockType(self):
        return "SimMks275GaugeFB"



    def simStructType(self):
        return "SimMks275GaugeStruct"



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
class EbaraDryPumpDevice(PumpDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "EBARADRYPUMP";



    def plcFunctionBlockType(self):
        return "EbaraDryPumpFB"



    def simFunctionBlockType(self):
         return "SimRoughPumpFB"



    def simStructType(self):
        return "SimRoughMechPumpStruct"


    
@register
class EbaraEvaPumpDevice(PumpDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "EBARAEVA";



    def plcFunctionBlockType(self):
        return "EbaraEvaPumpFB"



    def simFunctionBlockType(self):
         return "SimRoughPumpFB"



    def simStructType(self):
        return "SimRoughMechPumpStruct"


    
@register
class PtmTwisTorrPumpDevice(PumpDevice):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    @staticmethod
    def tag():
        return "PTM_TWISTORR";



    def plcFunctionBlockType(self):
        return "PtmTwisTorrPumpFB"


    
    def simFunctionBlockType(self):
        return "SimTurboPumpFB"



    def simStructType(self):
        return "SimTurboMechPumpStruct"


    
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


    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                "i_xExtIlkOK := TRUE, i_ReqPos := 0" +
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

        # check upstream gauge dependency for placeholder
        if self.upstreamGauge.startswith("?blank"):
            # replace placeholder with empty dependency, used for devices at boundary
            upstr = ""
        else:
            upGauge = self.container.getFB(self.upstreamGauge)
            if upGauge:
                upstr = upGauge.fbName + ".IG"
            else:
                sys.exit("device %s: unable to find upGauge: %s" %
                         (self.objectName(), self.upstreamGauge))
            
        # check downstream gauge dependency for placeholder
        if self.downstreamGauge.startswith("?blank"):
            # replace placeholder with empty dependency, used for devices at boundary
            downstr = ""
        else:
            downGauge = self.container.getFB(self.downstreamGauge)
            if downGauge:
                downstr = downGauge.fbName + ".IG"
            else:
                sys.exit("device %s: unable to find downGauge: %s" %
                         (self.objectName(), self.downstreamGauge))
            
        return (self.fbName +
                PlcGenerator.openParen +
                "i_stUSG := " +
                upstr +
                ", i_stDSG := " +
                downstr +
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
                PlcGenerator.openParen +
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
            sys.exit("device %s: unable to find ion gauge: %s" %
                     (self.objectName(), self.ionGauge))
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
            sys.exit("device %s: unable to find cold cathode gauge: %s" %
                     (self.objectName(), self.ccGauge))
        return (self.fbName +
                PlcGenerator.openParen +
                "i_stGauge := " +
                ccGauge.fbName + ".PG" +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def oType(self):
        return "FB_PIP_GAMMA";



class EbaraDryPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.bpGauge = deviceInfo.depGauge1 # adjacent pirani gauge



    def code(self):
        bpGauge = self.container.getFB(self.bpGauge)
        if ((not bpGauge)):
            sys.exit("device %s: unable to find pirani gauge: %s" %
                     (self.objectName(), self.bpGauge))
        return (self.fbName +
                PlcGenerator.openParen +
                "i_stBPGauge := " +
                bpGauge.fbName + ".PG" +
                ", i_xVlvOpn := TRUE, i_xExtIlkOK := TRUE" + 
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def oType(self):
        return "FB_EbaraDryPump";



class EbaraEvaPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                "i_xExtIlkOK := TRUE" + 
                PlcGenerator.closeParen +
                PlcGenerator.terminator)
    

    def oType(self):
        return "FB_EbaraEVA";



class PtmTwisTorrPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def code(self):
        return (self.fbName +
                PlcGenerator.openParen +
                "i_xExtILKOk := TRUE" +
                PlcGenerator.closeParen +
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
        upVol = self.container.getVolumeStruct(self.upstreamVolume)
        downVol = self.container.getVolumeStruct(self.downstreamVolume)
        valve = self.container.getStruct(self.valve)
        if ((not upVol) or (not downVol) or (not valve)):
            sys.exit("device %s: unable to find upVol: %s downVol: %s or valve: %s" %
                     (self.objectName(), self.upstreamVolume, self.downstreamVolume, self.valve))
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
        volume = self.container.getVolumeStruct(self.volume)
        gauge = self.container.getStruct(self.gauge)
        if ((not volume) or (not gauge)):
            sys.exit("device %s: unable to find volume: %s or gauge: %s" %
                     (self.objectName(), self.volume, self.gauge))
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
        volume = self.container.getVolumeStruct(self.volume)
        pip = self.container.getStruct(self.pip)
        if ((not volume) or (not pip)):
            sys.exit("device %s: unable to find volume: %s or pip: %s" %
                     (self.objectName(), self.volume, self.pip))
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



class SimRoughPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.inVol = deviceInfo.depVol1
        self.pump = deviceInfo.name



    def code(self):
        inVol = self.container.getVolumeStruct(self.inVol)
        pump = self.container.getStruct(self.pump)
        if ((not inVol) or (not pump)):
            sys.exit("device %s: unable to find inlet volume: %s or pump: %s" %
                     (self.objectName(), self.inVol, self.pump))
        return (self.fbName +
                PlcGenerator.openParen +
                "stVolInlet := " +
                inVol.structName +
                ", stPump := " +
                pump.structName +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

    def oType(self):
        return "FB_RoughPump";



class SimTurboPumpFB(PlcFunctionBlock):


    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)
        self.inVol = deviceInfo.depVol1
        self.outVol = deviceInfo.depVol2
        self.pump = deviceInfo.name



    def code(self):
        inVol = self.container.getVolumeStruct(self.inVol)
        outVol = self.container.getVolumeStruct(self.outVol)
        pump = self.container.getStruct(self.pump)
        if ((not inVol) or (not outVol) or (not pump)):
            sys.exit("device %s: unable to find inVol: %s outVol: %s or pump: %s" %
                     (self.objectName(), self.inVol, self.outVol, self.pump))
        return (self.fbName +
                PlcGenerator.openParen +
                "stVlInlet := " +
                inVol.structName +
                ", stVlOutlet := " +
                outVol.structName +
                ", stPump := " +
                pump.structName +
                PlcGenerator.closeParen +
                PlcGenerator.terminator)

    

    def oType(self):
        return "FB_TurboPump";



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




class SimRoughMechPumpStruct(PlcStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def declaration(self):

        return (self.objectName() + " : " +
                self.oType() + " := " +
                PlcGenerator.openParen +
                "rMRE:=10, rBasePress:=1E-3" +
                PlcGenerator.closeParen + PlcGenerator.terminator)

    def oType(self):
        return "ST_MechPump";



class SimTurboMechPumpStruct(PlcStruct):
    

    
    def __init__(self, deviceInfo):
        super().__init__(deviceInfo)



    def declaration(self):

        return (self.objectName() + " : " +
                self.oType() + " := " +
                PlcGenerator.openParen +
                "iMaxSpd:=1000, rBasePress:=1E-9, rMaxLoad:=0.95" +
                PlcGenerator.closeParen + PlcGenerator.terminator)

    

    def oType(self):
        return "ST_MechPump";



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


    
    def writeToFile(self, fobj, devOrdering):

        fobj.write("VAR_GLOBAL\n\n")
        super().writeToFile(fobj, devOrdering)                
        fobj.write("\nEND_VAR\n")
                



class ProgramDocument(PlcDocument):
    pass


    
class PlcContainer:



    otypeFB = "fb"
    otypeStruct = "st"
    otypeVolume = "vol"


    
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



    def addDevice(self, deviceName, deviceObj):
        plcFB = deviceObj.plcFunctionBlock()
        self.addFB(deviceName, plcFB)



    def addPlcObj(self, deviceName, plcType, plcObj):
        
        if not deviceName in self.plcDeviceMap:
            self.plcDeviceMap[deviceName] = {}
            
        if plcType in self.plcDeviceMap[deviceName]:
            # shouldn't already be a plc object in the map of this type for this device
            sys.exit("object of type: %s device: %s already in plcDeviceMap" % (plcType, deviceName))
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



    def addVolume(self, volName, progUnit):

        # add a simulation volume struct for this volume
        volumeInfo = DeviceInfo(volName,
                                "SIMVOLUME", "", "", "", "",
                                volName, "", "", progUnit)
        volumeStruct = SimVolumeStruct(volumeInfo)
        self.addVolumeStruct(volName, volumeStruct)

        # add the volume's info to list for sequential access
        self.volumes.append(volumeInfo)



    def addVolumeStruct(self, volName, volumeStruct):
        return self.addPlcObj(volName, self.otypeVolume, volumeStruct)



    def hasVolumeStruct(self, volName):
        return self.hasPlcObj(volName, self.otypeVolume)



    def getVolumeStruct(self, volName):
        return self.getPlcObj(volName, self.otypeVolume)



    # add simulation objects for this device
    def addDevice(self, deviceName, device):

        # create volumes associated with the device that don't yet exist
        for volName in [device.volume(), device.deviceInfo.depVol1, device.deviceInfo.depVol2]:
            if volName and volName != "":
                if not self.hasVolumeStruct(volName):
                    self.addVolume(volName, device.deviceInfo.progUnit)

        # add a simulation struct object for the device
        simStruct = device.simStruct()
        self.addStruct(deviceName, simStruct)

        # add a simulation function block object for the device
        simFB = device.simFunctionBlock()
        self.addFB(deviceName, simFB)



class PlcGenerator:


    
    openParen = "("
    closeParen = ")"
    terminator = ";"



    @classmethod
    def generatePlc(cls, container):

        # iterate through devices and create plc objects organized into files
        for devName in DeviceContainer.deviceList:
            device = DeviceContainer.deviceMap[devName]
            docName = device.progUnit()

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
            with open('gen.plc.GVL_' + docName.upper().replace("-", "_"), 'w') as f:
                document.writeToFile(f, deviceOrdering)

        # write program documents
        with open('gen.plc.PRG_MAIN', 'w') as fm:
            fm.write("PRG_DIAGNOSTIC();\n")
            for docName, document in container.progDocs.items():
                progName = 'PRG_' + docName.upper().replace("-", "_")
                with open('gen.plc.' + progName, 'w') as f:
                    document.writeToFile(f, deviceOrdering)
                    fm.write(progName + '();\n')

        # write non-PLC variables that are used in the PLC code created by the generator
        with open('gen.plc.GVL_VARIABLES', 'w') as f:
            f.write("xSystemOverrideMode : BOOL; (* Global system override for the prototype section*)\n")

        # write files for diagnostic code
        with open('gen.plc.PRG_DIAGNOSTIC.var', 'w') as f:
            f.write("   fbTime : FB_LocalSystemTime := ( bEnable := TRUE, dwCycle := 1 );\n" +
	            "   logTimer : TON := ( IN := TRUE, PT := T#1000ms );\n\n" +
	            "   plcName : STRING[15];\n\n" +	
	            "   {attribute 'pytmc' := ' pv: simHeartbeat '}\n" +
	            "   simHeartbeat AT %I* : UINT := 0;\n" +
	            "   {attribute 'pytmc' := ' pv: plcHeartbeat '}\n" +
	            "   plcHeartbeat : UDINT := 0;\n" +
	            "   {attribute 'pytmc' := ' pv: plcInfo '}\n" +
	            "   plcInfo : STRING[40];\n" +
	            "   {attribute 'pytmc' := ' pv: plcLocalTime '}\n" +
	            "   plcLocalTime : STRING[25];\n")

        with open('gen.plc.PRG_DIAGNOSTIC', 'w') as f:
            f.write("plcHeartbeat := plcHeartbeat + 1;\n" +
                    "IF plcHeartbeat > 4294967000\n" +
	            "   THEN plcHeartbeat := 0;\n" +
                    "END_IF\n\n" +
                    "// get timestamp as string every second\n" +
                    "fbTime();\n" +
                    "logTimer( IN := fbTime.bValid );\n" +
                    "IF logTimer.Q THEN\n" +
                    "   logTimer( IN := FALSE ); logTimer( IN := fbTime.bValid );\n" +
                    "   plcLocalTime := SYSTEMTIME_TO_STRING(fbTime.systemTime);\n" +
                    "END_IF\n\n" +
                    "// make an info string\n" +
                    "plcName := 'Prototype PLC: ';\n" +
                    "plcInfo := CONCAT(plcName, plcLocalTime);\n")


                
    @classmethod
    def generateSim(cls, container):

        # iterate through volumes and add declarations for volume structs
        for volInfo in container.volumes:

            volName = volInfo.name
            volStruct = container.getVolumeStruct(volName)
            
            decs = []
            decs.append(volStruct.declaration())
            progUnit = volInfo.progUnit
            container.addToVariablesDocument(progUnit, volStruct.oType(), decs)

        # iterate through devices and create plc objects organized into files
        for devName in DeviceContainer.deviceList:
            
            device = DeviceContainer.deviceMap[devName]
            docName = device.progUnit()

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
            with open('gen.sim.GVL_' + docName.upper().replace("-", "_"), 'w') as f:
                document.writeToFile(f, deviceOrdering)

        # write program documents
        with open('gen.sim.PRG_MAIN', 'w') as fm:
            fm.write("PRG_DIAGNOSTIC();\n")
            for docName, document in container.progDocs.items():
                progName = 'PRG_' + docName.upper().replace("-", "_")
                with open('gen.sim.' + progName, 'w') as f:
                    document.writeToFile(f, deviceOrdering)
                    fm.write(progName + '();\n')

        # write non-PLC variables that are used in the PLC code created by the generator
        with open('gen.sim.GVL_VARIABLES', 'w') as f:
            f.write("{attribute 'global_init_slot' := '40500'} // make sure variables are initialized before other GVLs\n")
            f.write("VAR_GLOBAL\n\n")
            f.write("Global_Leak : REAL := 0;\n")
            f.write("Global_Pressure : REAL := 0.0079;\n")
            f.write("New_Pressure : REAL := 22.0; //Torr\n")
            f.write("Global_OverridePressure : BOOL := FALSE;\n\n")
            f.write("END_VAR\n")

        # write files for diagnostic code
        with open('gen.sim.PRG_DIAGNOSTIC.var', 'w') as f:
            f.write("   heartbeat AT %Q* : UINT := 0;\n")

        with open('gen.sim.PRG_DIAGNOSTIC', 'w') as f:
            f.write("heartbeat := heartbeat + 1;\n" +
                    "IF heartbeat > 65000\n" +
	            "   THEN heartbeat := 0;\n" +
                    "END_IF\n")


                
    @classmethod
    def generateVarMap(cls, plcContainer, simContainer):

        # iterate through devices, adding a map entry for each
        simVarMap = {}
        for devName in DeviceContainer.deviceList:
            device = DeviceContainer.deviceMap[devName]
            plcFB = plcContainer.getFB(devName)
            simStruct = simContainer.getStruct(devName)          
            variableData = {}
            variableData['type'] = plcFB.oType()
            variableData['simVar'] = simStruct.objectName()
            simVarMap[plcFB.objectName()] = variableData
        
        with open('gen.varMap', 'wb') as f:
            pickle.dump(simVarMap, f, pickle.HIGHEST_PROTOCOL)

        

class DeviceHandler:



    progUnits = []
    devices = []
    supportedDevices = set()
    unsupportedDevices = set()


    
    @classmethod
    def handleDevice(cls, rowCount, info, plcContainer, simContainer, options):

        iProgUnit = info["PLC prog unit"]
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
        if (((not len(cls.devices)) and (not len(cls.progUnits))) or
            ((len(cls.devices)) and (iName in cls.devices)) or
            ((len(cls.progUnits)) and (iProgUnit in cls.progUnits))):

            # we are ignoring rows that don't have a tag, this allows the device info table to
            # contain devices that are out of scope of the plc, but generate a warning just in case:
            if ((not iTag) or (len(iTag) == 0)):
                print("skipping row with missing plc tag, row %d: %s" % (rowCount, info))
                return

            if ((not iName) or (len(iName) == 0)):
                sys.exit("no iName provided for row %d: %s" % (rowCount, info))

            if options.listTagsOnly:
                if PlcDevice.isSupported(iTag):
                    cls.supportedDevices.add(iTag)
                else:
                    cls.unsupportedDevices.add(iTag)

            else:

                devInfo = DeviceInfo(iName, iTag, iDepGauge1, iDepGauge2, iDepPump1,
                                     iDepValve1, iVolume, iDepVol1, iDepVol2, iProgUnit)

                device = PlcDevice.createDevice(iTag, devInfo)

                if (not device):
                    sys.exit("no device created for row %d: %s" % (rowCount, info))
                else:

                    # store device
                    DeviceContainer.addDevice(iName, device)

                    # store plc objects
                    if not options.simOnly:
                        plcContainer.addDevice(iName, device)

                    # store sim objects
                    if not options.plcOnly:
                        simContainer.addDevice(iName, device)
           

        
    @classmethod
    def printResult(cls, options):

        if options.listTagsOnly:
            
            # print all unique devices
            if len(cls.supportedDevices):
                print()
                print("supported devices:")
                for dtype in sorted(cls.supportedDevices):
                    print(dtype)
            if len(cls.unsupportedDevices):
                print()
                print("unsupported devices:")
                for dtype in sorted(cls.unsupportedDevices):
                    print(dtype)

        else:
            print("==================================================")
            print("SUMMARY")
            print("==================================================")
            print("devices created: %d" % len(DeviceContainer.deviceList))
        


class Options:



    def __init__(self):
        
        self.listTagsOnly = False
        self.plcOnly = False
        self.simOnly = False
 

        
def main():

    # process command line
    parser = argparse.ArgumentParser()
    parser.add_argument("deviceInfoFile", help="csv file with device info, expected format is first " +
                        "line with column names %s" % ("Device Name, PLC Tag, PLC dep gauge1, " +
                                                       "PLC dep gauge2, PLC dep pump1, PLC dep valve1, " +
                                                       "Volume, sim dep vol1, sim dep vol2"))
    parser.add_argument("--tags", help="list unique tag types for specified devices", action="store_true")
    parser.add_argument("--plc", help="generate plc artifacts only", action="store_true")
    parser.add_argument("--sim", help="generate sim artifacts only", action="store_true")
    parser.add_argument("--deviceFile", help="file containing devices to generate")
    parser.add_argument("--progUnitsFile", help="file containing program units to generate")
    args = parser.parse_args()

    options = Options()

    # make sure devInfo input file is specified
    if not args.deviceInfoFile:
        sys.exit("no device info file specified")
    else:
        print()
        print("using device info file: %s" % args.deviceInfoFile)

    # read optional list of volumes to create
    progUnitsFile = args.progUnitsFile
    if progUnitsFile:
        print()
        print("using program units file: %s" % progUnitsFile)
        try:
            with open(progUnitsFile, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    DeviceHandler.progUnits.append(row[0])
                print("program units file contains %d unit(s): %s" %
                      (len(DeviceHandler.progUnits), DeviceHandler.progUnits))
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
    if args.tags:
        options.listTagsOnly = True
        print()
        print("printing unique tags for specified devices")
        print()

    # for the plc and sim flags, we will generate only the corresponding artifacts
    if args.plc:
        options.plcOnly = True
        print()
        print("generating plc artifacts only")
        print()
    elif args.sim:
        options.simOnly = True
        print()
        print("generating sim artifacts only")
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
            DeviceHandler.handleDevice(rowCount, row, plcContainer, simContainer, options)

        # generate plc and sim code
        if not options.simOnly:
            PlcGenerator.generatePlc(plcContainer)
        if not options.plcOnly:
            PlcGenerator.generateSim(simContainer)

        if not options.simOnly and not options.plcOnly:
            PlcGenerator.generateVarMap(plcContainer, simContainer)

        # print summary
        DeviceHandler.printResult(options)



if __name__ == '__main__':
    main()
