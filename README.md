# pyplc
Contains two python programs, genPLC.py and mapSimIO.py.  The first takes a tabular device information table, and generates Beckhoff Twincat PLC code utilizing the vacuum device library created at SLAC.  The second takes output from genPLC.py, plus the Twincat tsproj xml file, and links the simulation PLC's variables to the simulated EtherCAT I/O devices, according to the links from the controls PLC's variable to I/O links.

## genPLC.py
### edit device info file
* for each device in the scope of the generator, edit the columns for capturing dependencies on other plc or sim devices (TODO: need to document each device)
### download device info file
* Find the device information table (e.g., https://drive.google.com/drive/folders/1PX-yMYoACvApI5ir16ePVcxCfJ65B_pj), and download the PLC worksheet as a csv file
* make sure the first row contains the columns: Area,PLC prog unit,Device Name,Device,PLC Tag,PLC dep gauge1,PLC dep gauge2,PLC dep pump1,PLC dep valve1,Volume,sim dep vol1,sim dep vol2 (column order doesn't matter)
* add device dependency placeholders for devices at boundary of section that you are going to generate code for, e.g., for the GMD, change the gauge 1 dependency for EM1K0-GMD-VGC-1 to ?blank#RTDS-GCC-1 and the gauge 2 dependency for TV1K0-GAS-VGC-1 to ?blank#AT1K0_GAS_GCC_10 . This tells the generator to create code that doesn't have a link to the target of the dependency since it is out of the scope of the generator.
### edit prog units file
* create a csv file with one column and no headings that contains a list of the program units that are in the scope of the generator - other units will be ignored, e.g.
```
GMD
```
### run genPLC.py to list supported and unsupported devices
Running the generator as follows will list supported and unsupported devices within the specified program unit(s):
```
python genPLC.py --progUnitsFile ./progUnits.gatt.csv ./device-info.gatt.csv --tags
```
This will display a list of supported and unsupported devices.  If there are unsupported devices, the next task is to modify the pyplc generator to support them.  This entails deriving a class from "PlcDevice", and implementing the appropriate methods, mostly class names for the associated PLC objects.  The best thing to do is find a similar pump, gauge, or valve, and copy that section as a starting point.  You'll need to implement methods that reference the PLC objects to create in the PLC and simulation code, a function block type for the PLC and both a struct and function block for the simulation.  So if your new device doesn't use existing PLC and simulation objects, you'll have to add those classes too, again using existing classes as a starting point.  It's all pretty straightforward.
### run genPLC.py
To run the generator using the device info and volumes csv files created above, to create just plc artifacts:
```
python genPLC.py --progUnitsFile ./progUnits.gmd.csv ./device-info.gmd.csv --plc
```
To run the generator using the device info and volumes csv files created above, to create just sim artifacts:
```
python genPLC.py --progUnitsFile ./progUnits.gmd.csv ./device-info.gmd.csv --sim
```
To run the generator using the device info and volumes csv files created above, to create plc and sim artifacts:
```
python genPLC.py --progUnitsFile ./progUnits.gmd.csv ./device-info.gmd.csv
```
Running the generator to create both plc and sim artifacts for the "GMD" program unit produces the following files:
```
gen.plc.GVL_GMD
gen.plc.GVL_VARIABLES
gen.plc.PRG_GMD
gen.plc.PRG_MAIN
gen.sim.GVL_GMD
gen.sim.GVL_VARIABLES
gen.sim.PRG_DIAGNOSTIC
gen.sim.PRG_DIAGNOSTIC.var
gen.sim.PRG_GMD
gen.sim.PRG_MAIN
gen.varMap
```
### create Twincat project for PLC and simulation
* run VisualStudio/Twincat, and create a new project
* from the "PLC" menu, use "Library Repository" to install the 3 SLAC-provided PLC libs, if they are not already present.  These are available in the github repo https://github.com/craigmcchesney/SLAC_vacuum_libs . Install each library file using the Library Repository tool.
#### create PLC
* under "PLC" node in solution explorer, add a new item of type "standard plc project", named "GmdPlc"
* expand the node for the new plc project, right click on "References", and select "add library", for both the "LCLS General" and "L2SI Vacuum Library" that you installed using the library repository, in the selection dialog these appear under the node labeled "Miscellaneous".  Also, search for the twincat library "Tc2_Utilities" and add that too.
* for each file created by the generator with the "gen.plc." prefix, create corresponding Twincat documents with the content from the generated files.  
  - note that the names of the files generated will vary depending on the program units specified to include in the scope of the generator
  - For each remaining file with a "gen.plc.GVL_" prefix (corresponding to the program units in the scope of the generator), add a new "Global Variable List" under the GVLs node of the sim project using the same program unit naming convention, and replace the default "{attribute 'qualified_only'}/VAR_GLOBAL/END_VAR" block with the content from the generated file.  For the GVL documents, be sure to remove the line at the top of the Twincat GVL file "{attribute 'qualified_only'}" so that variable references can be made from PLC programs without qualifying them using the GVL document name.  
  - The GVLs for this example should now include GVL_GMD and GVL_VARIABLES. 
  - For the file "gen.plc.PRG_MAIN", edit the already existing POU document "MAIN (PRG)", and add the file's content to the body of the program.  
  - For the files "gen.plc.PRG_DIAGNOSTIC.var" and gen.plc.PRG_DIAGNOSTIC", create the POU "PRG_DIAGNOSTIC", add the content of the file ending with ".var" to the VAR/END_VAR section at the top of the document, and then add the content of the other file as the body of the program.   
  - For the remaining files with "gen.plc.PRG_" prefix (corresponding to the program units in the scope of the generator), add a new POU element  using the same program unit naming convention and select structured text program as the type and paste in the generated file's content as the program code.  
  - The POUs for this example should include MAIN, PRG_DIAGNOSTIC, and PRG_GMD.  Note that this step will probably be automated at some point so that the generator produces xml files that can be added to the new project directly, but for now the process is manual.
* right click on the PLC project node and select "build", and ensure that the PLC builds without errors
#### create simulation
* under "PLC" node in solution explorer, add a new item of type "standard plc project", named "GmdSim"
* expand the node for the new plc project, right click on "References", and select "add library".  Under "Miscellaneous", select "Vacuum System Simulator Library" that you installed above, and click "OK".  Also, search for the twincat library "Tc2_Utilities" and add that too.
* as was done for the files prefixed with "gen.plc" above, add GVL and PRG documents for the files prefixed with "gen.sim".  
  - note that the names of the files generated will vary depending on the program units specified to include in the scope of the generator
  - For the file gen.sim.GVL_VARIABLES, add a new "Global Variable List" under the GVLs node of the sim project, and 
  - For each remaining file with a "gen.sim.GVL_" prefix (corresponding to the program units in the scope of the generator), add a new "Global Variable List" under the GVLs node of the sim project using the same program unit naming convention, and replace the default "{attribute 'qualified_only'}/VAR_GLOBAL/END_VAR" block with the content from the generated file.  For the GVL documents, be sure to remove the line at the top of the Twincat GVL file "" so that variable references can be made from PLC programs without qualifying them using the GVL document name.  
  - For this example, the GVLs for the simulation should include GVL_GMD and GVL_VARIABLES.  
  - For the file "gen.sim.MAIN", edit the already existing POU document "MAIN (PRG)", and add the file's content to the body of the program.  
  - For the files "gen.sim.PRG_DIAGNOSTIC.var" and gen.sim.PRG_DIAGNOSTIC", create the POU "PRG_DIAGNOSTIC", add the content of the file ending with ".var" to the VAR/END_VAR section at the top of the document, and then add the content of the other file as the body of the program.  
  - For the remaining files with "gen.sim.PRG_" prefix (corresponding to the program units in the scope of the generator), add a new POU element using the same program unit naming convention and select structured text program as the type and paste in the generated file's content as the program code.  
  - The POUs for this example should include MAIN, PRG_DIAGNOSTIC, and PRG_GMD.
* right click on the PLC project node and select "build", and ensure that the PLC builds without errors### save the PLC input/output variables to csv file
#### provide feedback for EPlan schematics
* for feedback to the EPlan schematics, we need to dump the PLC input and output variable names to a CSV file.  This allows us to later import the EPlan xml file to 1) create the I/O devices for the PLC, and link the PLC variables to the I/O devices.
* this step must be done after building the PLC project
* to save the input variables, expand the "Instance" node of your PLC project and double-click "PlcTask Inputs".  This displays a list of the input variables.  Select all the items in the list, right click, and select "save item as".  Specify the location and filename for the csv file that will contain the input variables.
* repeat the step above for the output variables, by double clicking on "PlcTask Outputs"
* provide these files AND THE NAME OF THE Twincat PLC, e.g., "GmdPlc" to the team member responsible for EPlan schematics, and ask them to provide you an EPlan xml export file.
### import xml file from EPlan using TC3 XCAD Interface
* install both Beckhoff “TwinCAT XAE” and “TC3 XCAD Interface” executables
```
https://infosys.beckhoff.com/content/1033/tc3_installation/index.html?id=2757066571859226971 
https://www.beckhoff.com/forms/twincat3/warenkorb2.aspx?id=1889849218918644160&lg=en&title=TE1120-TC3-XCAD-Interface&version=1.4.1.2 
```
* sync the PLC project repo from github (e.g., the project you created in the steps above):
```
https://github.com/craigmcchesney/GmdPlc 
```
* create a folder for the xcad import project
* download the EPlan generated XML file that you want to import to your xcad project folder
* clean up the xml file as necessary
  - remove all occurrences of the tags (usually with "X" or "Y") as the value
    ```
    <PreviousId></PreviousId>
    ```

* run “TwinCAT XAE” application which will run VisualStudio, and open the solution (sln file) inside the Twincat project folder that you synced from git, just to make sure the project loads
  - generate a TwinCAT license inside the Twincat XAE app (VisualStudio).  To do this, expand the “XtesSxrPlcProto” node in the left window pane, then expand the child node “SYSTEM” and double-click child node “License”.  Click button “7 Days Trial License”. Enter captcha value and click OK.  This should cause licenses for both “TC3 PLC” and “TC3 XCAD Interface” (and possibly others) to be listed in the table at the bottom of the middle window pane.  If "TC3 XCAD Interface" is not listed, click on the "Manage Licenses" tab and click the checkbox next to "TC3 XCAD Interface" in the "Add License" column, and check that the license now appears under the tab "Order Information (Runtime)".
  - close XAE
* run “TC3 XCAD Interface” application
  - DANGER: make sure you've made a backup of your twincat project.  The XCAD program will probably fail, and when it does, it will probably delete your ENTIRE twincat project, which can be disconcerting.  More details about how to (hopefully) restore it below.  But an extra backup can't hurt...
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
    * you can review the process output by clickingf the “Output” tab at the bottom of the pane, and errors by clicking “Error List”.  The output should show messages about producing xml for each node, and the error list should be empty.
    * click the toolbar button in the window's upper right corner to save the tci file
  - open “TwinCATImportFile.tci” in the xcad project folder using notepad
    * do “Find/Replace” to replace all occurrences of “XCAD_Interface_GVO.” (note the trailing period) (this could also be "XCAD_Interface_GVL.", it was GVO the first time I used the tool and GVL the 2nd) with an empty string (leave “to” field blank)
    * save the file, and click “Yes” to reload the local file instead of the one that xcad has been using
    * close notepad
  - select “ImportExport” from the tools menu
    * select radio button “Import data to an existing TwinCAT project” and click “Next” button
    * the path to the tci file should be displayed, check it and click “Next”
    * the path to the TwinCAT project you selected in the “new project” dialog should be displayed, check that it is or select it if not, and click “Next”
    * both paths are displayed for confirmation, review them and click “Next”
    * a dialog appears with console showing output from import process
    * the XAE/VisualStudio window opens, displaying the Twincat project
    * once the process is complete, the dialog displays the message “Import successfully completed. TwinCAT XAE will be closed now.  Save changes?”, regardless of whether the process was successful or not.
    * and also regardless of whether the process succeeded or not, the “Yes” button will be disabled
    * if you click “No”, the changes made by xcad to the twincat project will be lost
    * use the scrollbar in the import dialog to review the output.  there shouldn’t be errors about creating children, but there might be messages about linking failed if there are EPlan variables that can’t be mapped to twincat variables (e.g. right now there are EPlan output signals for the VGC pumps like TV2K4_VGC_1.q_xCLS_DO that don’t exist in twincat)
    * if (when) the process fails, you might receive a bunch of dialogs about backups failing and things not being "deleted in time".  You will probably find that your twincat project has been erased completely.  :-)  If you're lucky, you'll find it buried in your xcad project folder in a folder called "Backups", you might be able to just restore that folder to its original location.
    * the best thing to do is open the windows task manager using “ctrl-alt-del”, and then force kill TC3XCADInterface application whether it was successful or not.  If it was unsuccessful, you might want to dismiss the import/export dialog and go view the log file (select "View Log" from "Tools" menu).  This will give you an idea where to start troubleshooting.
  - if the import was successful, after killing the XCAD program, click over to the XAE/VisualStudio, otherwise see the troubleshooting section below
    * review the xcad changes e.g., 
      - that devices were added under the I/O node at the bottom of the project, and that the “PlcTask Inputs/Outputs” under “XtesSxrPlc Instance” are linked to devices.  You can double-click "PlcTask Inputs" and "PlcTask Outputs" to see a table of each function block variable.  The rightmost column shows what I/O channel that variable is linked to.  They should pretty much all be linked.
      - that a device tree is created under the "Devices" node of the project tree.  In this example, it is called "EK1100_00_00-CPU/EtherCAT1". Expand the nodes and compare the device tree to the input xml file used above.
    * from “File” menu, select “save all” to save the changes
#### troubleshooting
TC XCAD Interface is the worst tool ever created.  It crashes, fails for unspecified reasons, all lots of fun.  In the end, the crashes and failures usually claim that the user aborted the process but there is typically something about the input xml file that it's not happy about.  There is usually some red herring message about gui or events at the bottom of the import console or log viewer, but if you scroll up to where the last element of xml is mentioned "creating child x of y", there is probably something about element x that xcad doesn't like.  I've found it useful to compare that element to its predecessor(s) and see what is different about the element that is failing.  That's how I discovered the 2 problems below.
* in the most recent case, the following came up: had to remove all sections like:
```
       <Connection>
        <PreviousId>Y</PreviousId>
        <ConnectId>Y</ConnectId>
       </Connection>
```
* in a previous case, I had to remove sections like this:
```
<EtherCAT><Slave><Info><PhysAddr>1004</PhysAddr><PhysAddrFixed>true</PhysAddrFixed></Info><PreviousPort Selected="true"><PhysAddr>1003</PhysAddr></PreviousPort></Slave></EtherCAT>
```
In the end, Pedro changed something in the schematics and the problem went away, but it took a VERRRRRY LONG TIME to figure out what was wrong.  
```
The <PhysAddr>1003</PhysAddr> stuff was a variable in EPLAN that was filled out on some of the device when i placed them and thought i was necessary. These numbers seemed to impact the ordering and the tree structure of the PLC boxes when the xml to tci translation happened, so I number the box in order 1001 through 1006. I've deleted (left blank) these fields in EPLAN and now it seems to work.
```
### create a Twincat task to run the simulation
* under "GmdSim Project", right click "PlcTask (PlcTask)" and select delete to delete the default task
* under "System", right click "Tasks" and select "Add new item".  Name the new task "SimTask", and select Type "TwinCAT Task".  You'll see a new node "SimTask" under "Tasks"
* open SimTask and change its priority to 21, PLC tasks should be configured to run in the 20's, note that the main PlcTask created by default is set to 20.
* right click "GmdSim Project" and add a new "referenced task".  Select the "SimTask" that you just added and click "Open".  You'll now see a new node "SimTask (SimTask)" under "GmdSim Project".
* drag the GmdSim Project's "MAIN" POU to "SimTask (SimTask)", and now a node "MAIN" appears beneath it.  This means the MAIN program for the sim is now configured to run under SimTask.
### create EtherCAT simulation I/O devices from PLC I/O devices
* export the I/O devices for the PLC project
  - find the root device created in the XCAD import described above and select it.  From the "EtherCAT" tab in the content window, click "Export Configuration File". Select destination folder, name the file, and click "Save".
  - right click the "Devices" node under "I/O", and select "add new item". From the "Insert Device" dialog, select "EtherCAT Simulation", and name the new device e.g., "Sim Device 2".  For now, select "(none)" if prompted to select an ethernet device where the simulation i/o can be found.  We'll configure this later since it depends on the target system and not your development machine.  You should now see "SimDevice 2 (EtherCAT Simulation) under the root I/O device for the PLC.
  - Load the IO map for the simulation
    * right click on I/O / Devices /SimDevice 2 (EtherCAT Simulation) and selecing Import ENI file
    * select the xml file that you exported from the main I/O device above
    * expand the tree below "SimDevice2 (EtherCAT Simulation)" and you should see a device tree that looks more or less like the main I/O device for the PLC
### map the simulation variables to the simulation i/o devices
* create a working directory
* copy the ".tsproj" file for the Twincat project that you created above to the working directory
* copy the "gen.varMap" from the working directory for your generator run above to the working directory.  This is a serialized python dictionary that maps PLC variables to sim variables.  This is used to replicate the links from PLC variables to PLC I/O devices and create links between sim variables and sim I/O devices.  Otherwise this is a very tedious manual process.
* from the working directory, run the python mapper tool:
```
python mapSimIO.py GmdPlc.tsproj "TIPC^GmdPlc^GmdPlc Instance" "TIPC^GmdSim^GmdSim Instance" "SimTask" "TIID^SimDevice 2 (EtherCAT Simulation)^" gen.varMap
```
* make a backup of the original Twincat tsproj file in the directory where you copied it from originally since you are about to overwrite it with the one you just created.  The mapper program also creates a backup in the working directory with a ".bak.(timestamp)" extension
* copy the tsproj file written by the mapper (that now contains sim variable links) back to the Twincat project directory where you copied it from originally
* open your PLC project in Twincat and confirm that there are now links for the variables under "SimTask Inputs" and "SimTask Outputs".  Everything should be linked.
