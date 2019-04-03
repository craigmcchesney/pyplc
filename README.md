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
