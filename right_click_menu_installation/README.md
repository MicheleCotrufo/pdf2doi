The two batch files in this folder can be used to install and uninstall the shortcuts to pdf2doi in the context menu of Windows which appears when right-clicking on a .pdf file
or a directory

## Installation
First, make sure that pdf2doi has been installed as described in the readme of the main folder (```pip install pdf2doi```).
Then, locate the folder where the pdf2doi.exe file has been saved. This will depend on the folder of your python installation.
A simple way to find the folder is to type
```bash
where pdf2doi
```
from a command prompt (assuming that the path of pdf2doi is within the global variable PATH of the command prompt).

Save the file ```Install_RightClick.bat``` on your computer. Right click on it and select 'Edit'. The first line is
```bash
set path_pdf2doi=Path\To\Scripts
```
Replace 'Path\To\Scripts' with the path to the folder where pdf2doi.exe is. NOTE: Do not add the "\pdf2doi.exe" part.
If the path is, for example "C:\python38\scripts\pdf2doi.exe", then set
```bash
set path_pdf2doi=C:\python38\scripts
```

Run the file ```Install_RightClick.bat``` as an administrator (Right click on it, then click on "Run as administrator").

## Uninstallation
Save the file ```Uninstall_RightClick.bat``` on your computer and run it as administrator  (Right click on it, then click on "Run as administrator").

## Help
If for some reason the entries in the right-click context menu do not disappear after running ```Uninstall_RightClick.bat```,
open the system register manually and delete the following keys

```
HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi_bibtex
HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi_doi
HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi_setdoi
HKEY_CLASSES_ROOT\Directory\shell\pdf2doi_bibtex
HKEY_CLASSES_ROOT\Directory\shell\pdf2doi_doi
```
