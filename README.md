# pyplc
Contains two python programs, genPLC.py and mapSimIO.py.  The first takes a tabular device information table, and generates Beckhoff Twincat PLC code utilizing the vacuum device library created at SLAC.  The second takes output from genPLC.py, plus the Twincat tsproj xml file, and links the simulation PLC's variables to the simulated EtherCAT I/O devices, according to the links from the controls PLC's variable to I/O links.

## genPLC.py
### download device info file
* Find the device information table (e.g., https://drive.google.com/drive/folders/1PX-yMYoACvApI5ir16ePVcxCfJ65B_pj), and download the PLC worksheet as a csv file
* delete extra rows above the column headers, so the first row contains the columns: Area,Device Name,Device,PLC Tag,PLC dep gauge1,PLC dep gauge2,PLC dep pump1,PLC dep valve1,Volume,sim dep vol1,sim dep vol2
* add device dependency placeholders for devices at boundary of section that you are going to generate code for, e.g., for the GMD, change the gauge 1 dependency for EM1K0-GMD-VGC-1 to ?blank#RTDS-GCC-1 and the gauge 2 dependency for TV1K0-GAS-VGC-1 to ?blank#AT1K0_GAS_GCC_10 . This tells the generator to create code that doesn't have a link to the target of the dependency since it is out of the scope of the generator.
### edit volumes list file
* create a csv file with one column and no headings that contains a list of the volumes that are in the scope of the generator - other volumes will be ignored, e.g.
```
EM1K0-GMD-VGC-1
GMD
TV1K0-GAS-VGC-1
```
### run genPLC.py
To run the generator using the device info and volumes csv files created above:
```
python genPLC.py --volumeFile ./volumes-list.gmd.csv ./device-info.gmd.csv --plc
```
Note the --plc option tells the generator to produce code for the controls PLC only, skipping generation of the simulation artifacts.  Continuing the example above for the specified volumes, this produces the following files:
```
gen.plc.GVL_EM1K0_GMD_VGC_1
gen.plc.GVL_GMD
gen.plc.GVL_TV1K0_GAS_VGC_1
gen.plc.PRG_EM1K0_GMD_VGC_1
gen.plc.PRG_GMD
gen.plc.PRG_TV1K0_GAS_VGC_1
```
### create Twincat project for PLC
* run VisualStudio/Twincat, and create a new project
* from the "PLC" menu, use "Library Repository" to install the 3 SLAC-provided PLC libs, if they are not already present.  These are available in the github repo https://github.com/craigmcchesney/SLAC_vacuum_libs . Install each library file using the Library Repository tool.
* under "PLC" node in solution explorer, add a new item of type "standard plc project"
* expand the node for the new plc project, right click on "References", and select "add library", for both the "LCLS General" and "L2SI Vacuum Library" that you installed using the library repository, in the selection dialog these appear under the node labeled "Miscellaneous"
* for each file created by the generator with the "gen.plc." prefix, create corresponding Twincat documents with the content from the generated files.  For each file with a "GVL_" prefix, add a new "Global Variable List" under the GVLs node of the PLC project, and add the content from the generated file in the "VAR_GLOBAL" section.  For the GVL documents, be sure to remove the line at the top of the Twincat GVL file "{attribute 'qualified_only'}" so that variable references can be made from PLC programs without qualifying them using the GVL document name.  For the files with "PRG_" prefix, add a new POU element and select structured text program as the type and paste in the generated file's content as the program code.  The GVLs for the project should now include GVL_EM1K0_GMD_VGC_1, GVL_GMD, and GVL_TV1K0_GAS_VGC_1.  The POUs should include MAIN, PRG_EM1K0_GMD_VGC_1, PRG_GMD, and PRG_TV1K0_GAS_VGC_1.  Make sure to invoke each PRG_ file from the "MAIN" program as follows:
```
PRG_EM1K0_GMD_VGC_1();
PRG_GMD();
PRG_TV1K0_GAS_VGC_1();
```
Note that this step will probably be automated at some point so that the generator produces xml files that can be added to the new project directly, but for now the process is manual.
* add another GVL called "GVL_VARIABLES", and add the line ``	xSystemOverrideMode : BOOL;`` in the "VAR_GLOBAL" section.
* right clock on the PLC project node and select "build", and ensure that the PLC builds without errors
