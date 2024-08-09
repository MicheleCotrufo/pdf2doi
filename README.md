# pdf2doi 

```pdf2doi``` is a Python library/command-line tool to automatically extract the DOI or other identifiers (e.g. arXiv ID) starting from the .pdf file of a publication 
(or from a folder containing several .pdf files), and to retrieve bibliographic information.
It exploits several methods (see below for detailed description) to find a valid identifier of a pdf file, and it validates any result
via web queries to public archives (e.g. http://dx.doi.org). 
The validation process also returns raw bibtex infos, which can be used for further processing, such as generating BibTeX entries ([pdf2bib](https://github.com/MicheleCotrufo/pdf2bib)) or
automatically renaming pdf files ([pdf-renamer](https://github.com/MicheleCotrufo/pdf-renamer)).

pdf2doi can be used either from [command line](#command-line-usage), or inside your [python script](#usage-inside-a-python-script) or, only for Windows, directly from the [right-click context menu](#installing-the-shortcuts-in-the-right-click-context-menu-of-windows) of a pdf file or a folder.

[![Downloads](https://pepy.tech/badge/pdf2doi)](https://pepy.tech/project/pdf2doi?versions=1.4&versions=1.5.post1&versions=1.6)
[![Downloads](https://pepy.tech/badge/pdf2doi/month)](https://pepy.tech/project/pdf2doi?versions=1.4&versions=1.5.post1&versions=1.6)
[![Pip Package](https://img.shields.io/pypi/v/pdf2doi?logo=PyPI)](https://pypi.org/project/pdf2doi)

## Warning
Versions of ```pdf2doi``` prior to the **1.6** are affected by a very annoying bug. By default, after finding the DOI of a pdf paper, ```pdf2doi``` will store the DOI into the metadata of the pdf file. Due to a bug, the size of the pdf file would double everytime that a metadata was added. This bug has been fixed in all versions >= 1.6. 

If you have pdf files that have been affected by this bug, you can use ```pdf2doi``` to fix it. After updating to a version > 1.6, run ```pdf2doi path/to/folder/containing/pdf/files -id ''```. This will restore the pdf files to their original size.

Thanks Ole Steuernagel for pointing out this issue.

## Latest stable version
The latest stable version of ```pdf2doi``` is the **1.6**. See [here](https://github.com/MicheleCotrufo/pdf2doi/releases) for the full change log.

### [v1.6] - 2024-06-18

#### Main changes
- The library ```pypdf``` is now used (instead of ```PyPdf2```) to add new metadata to the pdf files (see also fix below). Since ```PyPdf2``` is now deprecated, in the next version of ```pdf2doi``` we will progressively replace all tasks performed by ```PyPdf2``` by ```pypdf``` 

#### Added
- Make sure that the input variable target is converted to a string before processing https://github.com/MicheleCotrufo/pdf2doi/pull/27

#### Fixed
- Fixed a bug related to the storing of the DOI into the metadata of the pdf files. Due to some quirks of the library ```PyPdf2```, the size of the pdf file would double after adding the metadata. In this new version, adding metadata to a pdf file is now performed via the library ```pypdf``` (Thanks Ole Steuernagel for pointing out this issue).

## Installation

Use the package manager pip to install pdf2doi.

```bash
pip install pdf2doi==1.6
```

The library ```textract``` provides additional ways to analyze pdf files, and it is sometimes more powerful than ```PyPDF2```, but it comes with a large overhead of additional required dependencies, and sometimes it generates version conflicts. 
The user can decide whether to install it or not. ```pdf2doi``` will only try to use this library if it detects that it is installed.
To install it,
```bash
pip install textract==1.6.4
pip install pdfminer.six==20191110
```

Under Windows, after installation of ```pdf2doi``` it is also possible to add [shortcuts to the right-click context menu](#installing-the-shortcuts-in-the-right-click-context-menu-of-windows).

## Used by

Here is a list of applications/repositories that make use of ```pdf2doi```. If you use ```pdf2doi``` in your application and you wish to add it to this list, send me a message.

* [file_organizer](https://github.com/codedai/file_organizer)
* [pubmex](https://github.com/mmagnus/pubmex)
* [mendeley-migration](https://github.com/newmanrs/mendeley-migration)
* [pub2sum](https://github.com/SamuelKnaus/pub2sum)
* [DataIngest](https://github.com/workfor-webapps/DataIngest)
* [pdf2bib](https://github.com/MicheleCotrufo/pdf2bib)
* [pdf-renamer](https://github.com/MicheleCotrufo/pdf-renamer)


## Table of Contents
 - [Installation](#installation)
 - [Description](#description)
 - [Usage](#usage)
    * [Command line usage](#command-line-usage)
        + [Manually associate the correct identifier to a file from command line](#manually-associate-the-correct-identifier-to-a-file-from-command-line)
    * [Usage inside a python script](#usage-inside-a-python-script)
        + [Manually associate the correct identifier to a file](#manually-associate-the-correct-identifier-to-a-file)
 - [Installing the shortcuts in the right-click context menu of Windows](#installing-the-shortcuts-in-the-right-click-context-menu-of-windows)
  -[Contributing](#contributing)
 - [License](#license)
 - [Acknowledgment](#acknowledgment)
 - [Donating](#donating)

## Description
Automatically associating a DOI or other identifiers (e.g. arXiv ID) to a pdf file can be either a very easy or a very difficult
(sometimes nearly impossible) task, depending on how much care was placed in crafting the file. In the simplest case (which typically works with most recent publications)
it is enough to look into the file metadata. For older publications, the identifier is often found within the pdf text and it can be
extracted with the help of regular expressions. In the unluckiest cases, the only method left is to google some details of the publication
(e.g. the title or parts of the text) and hope that a valid identifier is contained in one of the first results.

```pdf2doi``` applies sequentially all these methods (starting from the simplest ones) until a valid identifier is found and validated.
Specifically, for a given .pdf file it will, in order,

1. Look into the metadata of the .pdf file (extracted via the library [PyPDF2](https://github.com/mstamy2/PyPDF2)) and check if any of them contains a string that matches the pattern of 
a DOI or an arXiv ID. Priority is given to metadata which contain the word 'doi' in their label.

2. Check if the name of the pdf file contains any sub-string that matches the pattern of 
a DOI or an arXiv ID.

3. Scan the text inside the .pdf file, and check for any string that matches the pattern of 
a DOI or an arXiv ID. The text is extracted with the libraries [PyPDF2](https://github.com/mstamy2/PyPDF2) and [pdfminer](https://github.com/pdfminer/pdfminer.six). If the library 
[textract](https://github.com/deanmalmgren/textract) is installed, ```pdf2doi``` will try to use that too.

4. Try to find possible titles of the publication. In the current version, possible titles are identified via 
the libraries [pdftitle](https://github.com/metebalci/pdftitle) and [PyMuPDF](https://github.com/pymupdf/PyMuPDF), and by the file name. For each possible title a google search 
is performed and the plain text of the first results is scanned for valid identifiers.

5. As a last desperate attempt, the first N=1000 characters of the pdf text are used as a query for
a google search. The plain text of the first results is scanned for valid identifiers.

Any time that a potential identifier is found, it is also validated by performing a query to a relevant website (e.g., http://dx.doi.org for DOIs and http://export.arxiv.org for arxiv IDs). 
This validation process also returns raw [BibTeX](http://www.bibtex.org/) info when the identifier is valid. 

When a valid identifier is found with any method different than the first one, the identifier is also stored inside the metadata of
the pdf file. In this way, future lookups of this same file will be able to extract the identifier with the 
first method, speeding up the search (This feature can be disabled by the user, in case edits to the pdf file are not desired).

The library is far from being perfect. Often, especially for old publications, none of the currently implemented methods will work. Other times the wrong DOI might be extracted: this can happen, for example, 
if the DOI of another paper is present in the pdf text and it appears before the correct DOI. A quick and dirty solution to this problem is to look up the identifier manually and then add it to the metadata
of the file, with the methods shown [here](#manually-associate-the-correct-identifier-to-a-file) (from python console) or [here](#manually-associate-the-correct-identifier-to-a-file-from-command-line) (from command line). 
In this way, ```pdf2doi``` will always retrieve the correct DOI when analyzing this same file in the future, which can be useful when ```pdf2doi```  is used  to automatize
 bibliographic procedures for a large number of files (e.g. via [pdf2bib](https://github.com/MicheleCotrufo/pdf2bib) or
[pdf-renamer](https://github.com/MicheleCotrufo/pdf-renamer)).

Currently, only the format of arXiv identifiers in use after [1 April 2007](https://arxiv.org/help/arxiv_identifier) is supported.

## Usage

pdf2doi can be used either as a [stand-alone application](#command-line-usage) invoked from the command line, or by [importing it in your python project](#usage-inside-a-python-script) or, only for Windows, 
directly from the [right-click context menu](#installing-the-shortcuts-in-the-right-click-context-menu-of-windows) of a pdf file or a folder.

### Command line usage
```pdf2doi``` can be invoked directly from the command line, without having to open a python console.
The simplest command-line invokation is

```.
$ pdf2doi 'path/to/target'
```
where ```target``` is either a valid pdf file or a directory containing pdf files. Adding the optional command '-v' increases the output verbosity,
documenting all steps.
For example, when targeting the folder [examples](/examples) we get the following output

```
$ pdf2doi ".\examples" -v
[pdf2doi]: Looking for pdf files in the folder ....
[pdf2doi]: Found 4 pdf files.
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\chaumet_JAP_07.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Validating the possible DOI 10.1063/1.2409490 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1063/1.2409490 is validated by dx.doi.org.
[pdf2doi]: A valid DOI was found in the document text.
[pdf2doi]: Trying to add the tag '/pdf2doi_identifier'-> '10.1063/1.2409490' into the metadata of the file '.\chaumet_JAP_07.pdf'...
[pdf2doi]: The tag '/pdf2doi_identifier'-> '10.1063/1.2409490' was added succesfully to the metadata of the file '.\chaumet_JAP_07.pdf'...
[pdf2doi]: 10.1063/1.2409490
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\paper12.2009_unknown_040916_440842.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Could not find a valid identifier in the document text extracted by PyPdf.
[pdf2doi]: Extracting text with the library pdfminer...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Validating the possible DOI 10.1037/a0015278 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1037/a0015278 is validated by dx.doi.org.
[pdf2doi]: A valid DOI was found in the document text.
[pdf2doi]: Trying to add the tag '/pdf2doi_identifier'-> '10.1037/a0015278' into the metadata of the file '.\paper12.2009_unknown_040916_440842.pdf'...
[pdf2doi]: The tag '/pdf2doi_identifier'-> '10.1037/a0015278' was added succesfully to the metadata of the file '.\paper12.2009_unknown_040916_440842.pdf'...
[pdf2doi]: 10.1037/a0015278
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\PhysRevLett.116.061102.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Standardised DOI: 10.1103/PhysRevLett.116.061102 -> 10.1103/physrevlett.116.061102
[pdf2doi]: Validating the possible DOI 10.1103/physrevlett.116.061102 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1103/physrevlett.116.061102 is validated by dx.doi.org.
[pdf2doi]: Standardised DOI: 10.1103/PhysRevLett.116.061102 -> 10.1103/physrevlett.116.061102
[pdf2doi]: A valid DOI was found in the document text.
[pdf2doi]: Trying to add the tag '/pdf2doi_identifier'-> '10.1103/physrevlett.116.061102' into the metadata of the file '.\PhysRevLett.116.061102.pdf'...
[pdf2doi]: The tag '/pdf2doi_identifier'-> '10.1103/physrevlett.116.061102' was added succesfully to the metadata of the file '.\PhysRevLett.116.061102.pdf'...
[pdf2doi]: 10.1103/physrevlett.116.061102
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\s41586-019-1666-5.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Validating the possible DOI 10.1038/s41586-019-1666-5 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1038/s41586-019-1666-5 is validated by dx.doi.org.
[pdf2doi]: A valid DOI was found in the document text.
[pdf2doi]: Trying to add the tag '/pdf2doi_identifier'-> '10.1038/s41586-019-1666-5' into the metadata of the file '.\s41586-019-1666-5.pdf'...
[pdf2doi]: The tag '/pdf2doi_identifier'-> '10.1038/s41586-019-1666-5' was added succesfully to the metadata of the file '.\s41586-019-1666-5.pdf'...
[pdf2doi]: 10.1038/s41586-019-1666-5
[pdf2doi]: ................
DOI             10.1063/1.2409490                        .\chaumet_JAP_07.pdf

DOI             10.1037/a0015278                         .\paper12.2009_unknown_040916_440842.pdf

DOI             10.1103/physrevlett.116.061102           .\PhysRevLett.116.061102.pdf

DOI             10.1038/s41586-019-1666-5                .\s41586-019-1666-5.pdf
```

Every line which begins with ```[pdf2doi]``` is omitted when the optional command '-v' is absent.
In the final output, the first column specifies the kind of identifier (currently either 'DOI' or 'arxiv'), the second column contains the found DOI/identifier, and the third column contains the file path.


A list of all optional arguments can be generated by ```pdf2doi --h```
```
$ pdf2doi --h
usage: pdf2doi [-h] [-v] [-nws] [-nwv] [-nostore] [-no_arxiv2doi] [-id IDENTIFIER] [-google GOOGLE_RESULTS] [-s FILENAME_IDENTIFIERS] [-clip] [-install--right--click] [-uninstall--right--click] [path ...]

Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a publications.

positional arguments:
  path                  Relative path of the target pdf file or of the targe folder.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase verbosity. By default (i.e. when not using -v), only a table with the found identifiers will be printed as output.
  -nws, --no_web_search
                        Disable any method to find identifiers which requires internet searches (e.g. queries to google).
  -nwv, --no_web_validation
                        Disable the online validation of identifiers (e.g., via queries to http://dx.doi.org/).
  -nostore, --no_store_identifier_metadata
                        By default, anytime an identifier is found it is added to the metadata of the pdf file (if not present yet). By using this additional option, the identifier is not stored in the file
                        metadata.
  -no_arxiv2doi         If a valid arXiv ID is found for a given .pdf file, by default pdf2doi will try to also look for a DOI (either because the paper has been published in a journal or because arXiv has
                        assigned to it a DOI of the form "10.48550/arXivID"). By adding this command, the arXiv ID is instead always returned.
  -id IDENTIFIER        Stores the string IDENTIFIER in the metadata of the target pdf file, with key '/pdf2doi_identifier'. Note: when this argument is passed, all other arguments (except for the path to the
                        pdf file) are ignored.
  -google GOOGLE_RESULTS
                        Set how many results should be considered when doing a google search for the DOI (default=6).
  -s FILENAME_IDENTIFIERS, --save_identifiers_file FILENAME_IDENTIFIERS
                        Save all the identifiers found in the target folder in a text file inside the same folder with name specified by FILENAME_IDENTIFIERS. This option is only available when a folder is
                        targeted.
  -clip, --save_doi_clipboard
                        Store all found DOI/identifiers into the clipboard.
  -install--right--click
                        Add a shortcut to pdf2doi in the right-click context menu of Windows. You can copy the identifier and/or bibtex entry of a pdf file (or all pdf files in a folder) into the clipboard by
                        just right clicking on it! NOTE: this feature is only available on Windows.
  -uninstall--right--click
                        Uninstall the right-click context menu functionalities. NOTE: this feature is only available on Windows.
```

#### Manually associate the correct identifier to a file from command line
Sometimes it is not possible to retrieve a DOI/identifier automatically, or maybe the one that is retrieved is not the correct one. In these (hopefully rare) occasions
it is possible to manually add the correct DOI/identifier to the pdf metadata, by using the ```-id``` argument,
```
$ pdf2doi "path\to\pdf" -id "doi1234"
```
This creates a new metadata in the pdf file with label '/pdf2doi_identifier' and containing the string ```doi1234```.  Future lookups of this same file via ```pdf2doi``` (in particular when used by other tools such as [pdf2bib](https://github.com/MicheleCotrufo/pdf2bib) or
[pdf-renamer](https://github.com/MicheleCotrufo/pdf-renamer)) will then return the correct identifier and BibTeX infos.

### Usage inside a python script
```pdf2doi``` can also be used as a library within a python script. The function ```pdf2doi.pdf2doi``` is the main point of entry. The function looks for the identifier of a pdf file by applying all the available methods. 
The first input argument must be a valid path (either absolute or relative) to a pdf file or to a folder containing pdf files. The path can be passed either as a string, or as a Pathlib object 
The same optional arguments available in the command line operation are now available via the methods ```set``` and ```get``` of the object ```pdf2doi.config```
For example, we can scan the folder [examples](/examples) while soppressing output verbosity by, 

```python
>>> import pdf2doi
>>> pdf2doi.config.set('verbose',False)
>>> results = pdf2doi.pdf2doi('.\examples')
```
A full list of the library settings can be printed by the method ```pdf2doi.config.print()```
```python
>>> import pdf2doi
>>> pdf2doi.config.print()
verbose : True (bool)
separator : \ (str)
method_dxdoiorg : application/citeproc+json (str)
webvalidation : True (bool)
websearch : True (bool)
numb_results_google_search : 6 (int)
N_characters_in_pdf : 1000 (int)
save_identifier_metadata : True (bool)
replace_arxivID_by_DOI_when_available : True (bool)
```

The output of the function ```pdf2doi``` is a list of dictionaries (or just a single dictionary if a single file was targeted). Each dictionary has the following keys

```python
result['identifier'] = DOI or other identifier (or None if nothing is found)
result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
result['validation_info'] = Additional info on the paper. If config.get('webvalidation') = True, then result['validation_info']
                            will typically contain raw bibtex data for this paper. Otherwise it will just contain True 
result['path'] = path of the pdf file
result['method'] = method used to find the identifier
```
For example, the DOIs/identifiers of each file can be printed by
```python
>>> for result in results:
>>>     print(result['identifier'])
10.1016/0021-9991(86)90093-8
10.1063/1.2409490
10.1103/PhysRevLett.116.061102
10.1038/s41586-019-1666-5
```

By default, everytime that a valid DOI/identifier is found, it is stored in the metadata of the pdf file. In this way, subsequent lookups of the same folder/file will be much faster.
This behaviour can be removed (e.g. if the user does not want or cannot edit the files) by setting save_identifier_metadata to False, via
```python
>>> pdf2doi.config.set('save_identifier_metadata',False)
```

#### Manually associate the correct identifier to a file
Similarly to what described [above](#manually-associate-the-correct-identifier-to-a-file-from-command-line), it is possible to associate a (manually found) 
identifier to a pdf file also from within python, by using the function ```pdf2doi.add_found_identifier_to_metadata```:

```python
>>> import pdf2doi
>>> pdf2doi.add_found_identifier_to_metadata(path_to_pdf_file, identifier)
```
this creates a new metadata in the pdf file with label '/pdf2doi_identifier' and containing the string ```identifier```.  

## Installing the shortcuts in the right-click context menu of Windows
This functionality is only available on Windows (and so far it has been tested only on Windows 10). It adds additional commands to the context menu of Windows
which appears when right-clicking on a pdf file or on a folder.
<!--
<img src="docs/ContextMenu_pdf.png" width="550" /><img src="docs/ContextMenu_folder.png" width="550" />
-->
The different menu commands allow to copy the paper(s) identifier(s) into the system clipboard, or also to manually
set the identifier of a pdf file (see also [here](#manually-associate-the-correct-identifier-to-a-file-from-command-line)).
<!--
<img src="docs/ContextMenu_pdf.gif" width="500" />
-->
To install this functionality, first install ```pdf2doi``` via pip (as described above), then open a command prompt **with administrator rights** and execute
```
$ pdf2doi  -install--right--click
```
To remove it, simply run (again from a terminal with administrator rights)
```
$ pdf2doi  -uninstall--right--click
```
If it is not possible to run this command from a terminal with administrator rights, the batch files
[here](/right_click_menu_installation) can be alternatively used (see readme.MD file in the same folder for instructions), although it is still required to have 
admnistrator rights.

NOTE: when multiple pdf files are selected, and the right-click context menu commands are used, ```pdf2doi``` will be called separately for each file, and thus
only the info of the last file will be stored in the clipboard. In order to copy the info of multiple files it is necessary to save them in a folder and right-click on the folder.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgment
I am thankful to my friend and colleague Yarden Mazor for leading the beta-testing efforts for this project.

## Donating
If you find this library useful (or amazing!), please consider making donations on my behalf to organizations that advocate for and promote free dissemination of science, such as

[arXiv](https://arxiv.org/about/donate)

[Sci-Hub](https://sci-hub.se/donate)

[Wikipedia](https://donate.wikimedia.org/)


## License
[MIT](https://choosealicense.com/licenses/mit/)

