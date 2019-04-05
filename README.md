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
* right click on the PLC project node and select "build", and ensure that the PLC builds without errors
### save the PLC input/output variables to csv file
* for feedback to the EPlan schematics, we need to dump the PLC input and output variable names to a CSV file.  This allows us to later import the EPlan xml file to 1) create the I/O devices for the PLC, and link the PLC variables to the I/O devices.
* this step must be done after building the PLC project
* to save the input variables, expand the "Instance" node of your PLC project and double-click "PlcTask Inputs".  This displays a list of the input variables.  Select all the items in the list, right click, and select "save item as".  Specify the location and filename for the csv file that will contain the input variables.
* repeat the step above for the output variables, by double clicking on "PlcTask Outputs"
* provide these files to the team member responsible for EPlan schematics, and ask them to provide you an EPlan xml export file.
### import xml file from EPlan using TC3 XCAD Interface
* install both Beckhoff “TwinCAT XAE” and “TC3 XCAD Interface” executables
```
https://infosys.beckhoff.com/content/1033/tc3_installation/index.html?id=2757066571859226971 
https://www.beckhoff.com/forms/twincat3/warenkorb2.aspx?id=1889849218918644160&lg=en&title=TE1120-TC3-XCAD-Interface&version=1.4.1.2 
```
* sync the PLC project repo from github:
```
https://github.com/craigmcchesney/XTES-SXR-vacuum-PLC-prototype 
```
* create a folder for the xcad import project
* download the EPlan generated XML file that you want to import to your xcad project folder e.g., 
```
https://drive.google.com/file/d/133y2T59sPIvZixEH33l8fZKdpjWKky7Q/view 
```
* run “TwinCAT XAE” application which will run VisualStudio, and open the solution (sln file) inside the Twincat project folder that you synced from git, just to make sure the project loads
  - generate a TwinCAT license inside the Twincat XAE app (VisualStudio).  To do this, expand the “XtesSxrPlcProto” node in the left window pane, then expand the child node “SYSTEM” and double-click child node “License”.  Click button “7 Days Trial License”. Enter captcha value and click OK.  This should cause licenses for both “TC3 PLC” and “TC3 XCAD Interface” (and possibly others) to be listed in the table at the bottom of the middle window pane.
  - close XAE
* run “TC3 XCAD Interface” application
  - select “New Project” from File menu
    * in the dialog that appears, for “Location”, browse to xcad project folder created above
    * for “CAD export file”, select the xml file downloaded above
    * for “TwinCAT project”, select the “sln” file in the XAE project folder synced from github
    * click “Save” button
  - a tree representation of the xml file is displayed in the left window pane
  - from “Tools” menu, select “Settings”
    * in left-side tree view, select “Transformation” child of “Settings”
    * make sure “Generate PLC project” is set to “False” and click “OK”
  - click the button with an arrow pointing to the right between the left and right window panes
    * this runs a transformation and now a tree representation of the resulting “tci” file is displayed in the right window pane
    * you can review the process output by click the “Output” tab at the bottom of the pane, and errors by clicking “Error List”.  The output should show messages about producing xml for each node, and the error list should be empty.
    * click the toolbar button to save the tci file
  - open “TwinCATImportFile.tci” in the xcad project folder using notepad
    * do “Find/Replace” to replace all occurrences of “XCAD_Interface_GVO.” (note the trailing period) (this could also be "XCAD_Interface_GVL.", it was GVO the first time I used the tool and GVL the 2nd) with an empty string (leave “to” field blank)
    * save the file, and click “Yes” to reload the local file instead of the one that xcad has been using
    * close notepad
  - select “ImportExport” from the tools menu
    * click “Yes” button to save the “tci” file
    * at this point, you can open the “tci” file in notepad and review the xml that will be imported to twincat.  You don’t need to do this but for experimental work you might want to
    * select radio button “Import data to an existing TwinCAT project” and click “Next” button
    * the path to the tci file should be displayed, check it and click “Next”
    * the path to the TwinCAT project you selected in the “new project” dialog should be displayed, check that it is or select it if not, and click “Next”
    * both paths are displayed for confirmation, review them and click “Next”
    * a dialog appears with console showing output from import process
    * the XAE/VisualStudio window opens, displaying the Twincat project
    * once the process is complete, it displays the message “Import successfully completed. TwinCAT XAE will be closed now.  Save changes?”, regardless of whether the process was successful or not.
    * and also regardless of whether the process succeeded or not, the “Yes” button will be disabled
    * if you click “No”, the changes made by xcad to the twincat project will be lost
use the scrollbar in the import dialog to review the output.  there shouldn’t be errors about creating children, but there might be messages about linking failed if there are EPlan variables that can’t be mapped to twincat variables (e.g. right now there are EPlan output signals for the VGC pumps like TV2K4_VGC_1.q_xCLS_DO that don’t exist in twincat)
    * the best thing to do is open the windows task manager using “ctrl-alt-del”, and then force kill TC3XCADInterface application.
  - click over to the XAE/VisualStudio, 
    * review the xcad changes e.g., that devices were added under the I/O node at the bottom of the project, and that the “PlcTask Inputs/Outputs” under “XtesSxrPlc Instance” are linked to devices by double clicking on each device and checking that its “Linked to…” field shows a non-empty value.  Currently some variables do not get linked because they don’t exist in the EPlan schematic.  This varies by device and we are working to understand these.
    * from “File” menu, select “save all” to save the changes
