# pdf2doi

pdf2doi is a Python library to extract the DOI or other identifiers (e.g. arXiv) starting from the .pdf file of a publication (or from a folder containing several .pdf files).
It exploits several methods (see below for detailed description) to find a possible identifier, and it validates any result
via web queries to public archives (e.g. http://dx.doi.org). Additionally, it allows generating automatically bibtex entries.

## Description
Automatically associating a DOI or other identifiers (e.g. arXiv) to a pdf file can be either a very easy or a very difficult
(something nearly impossible) task, depening on how much care was placed in crafting the file. 

The ```pdf2doi``` library applies systematically  different methods (starting from the simpler one) until a valid identifier is found and validated.
Specifically, for a given .pdf file it will, in order,

1. Look into the metadata of the .pdf file (extracted via the library [PyPDF2](https://github.com/mstamy2/PyPDF2)) and see if any string matches the pattern of 
a DOI or an arXiv ID. Priority is given to the metadata which contain the words 'doi' in their name.

2. Check if the file name (i.e. 'filename.pdf') contains any sub-string that matches the pattern of 
a DOI or an arXiv ID.

3. Scan the text inside the .pdf file, and check for any string that matches the pattern of 
a DOI or an arXiv ID. The text is extracted with the libraries [PyPDF2](https://github.com/mstamy2/PyPDF2) and [textract](https://github.com/deanmalmgren/textract).

4. Try to find possible titles of the publication. In the current version, possible titles are identified via 
the library [pdftitle](https://github.com/metebalci/pdftitle "pdftitle"), and by the file name. For each possible title a google search 
is performed and the plain text of the first results is scanned for valid identifiers.


## Installation

Use the package manager [pip] to install pdf2doi.

```bash
pip install pdf2doi
```

## Usage

pdf2doi can be used either as a stand-alone application invoked from the command line, or by importing it in your python project.

### Command line usage:

```
pdf2doi 'path/filename.pdf'
pdf2doi './folder'
```
```

>> pdf2doi --h
usage: pdf2doi [-h] [-v] [-nws] [-nwv] [-google_results GOOGLE_RESULTS] [-s [FILENAME_IDENTIFIERS]] [-b [FILENAME_BIBTEX]] path

Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a publications.

positional arguments:
  path                  Relative path of the pdf file or of a folder.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity.
  -nws, --nowebsearch   Disable any DOI retrieval method which requires internet searches (e.g. queries to google).
  -nwv, --nowebvalidation
                        Disable the DOI online validation via queries (e.g., to http://dx.doi.org/).
  -google_results GOOGLE_RESULTS
                        Set how many results should be considered when doing a google search for the DOI (default=6).
  -s [FILENAME_IDENTIFIERS], --save_identifiers [FILENAME_IDENTIFIERS]
                        Save all the DOIs/identifiers found in the target folder in a .txt file inside the same folder (only available when a folder is targeted).
  -b [FILENAME_BIBTEX], --make_bibtex [FILENAME_BIBTEX]
                        Create a file with bibtex entries for each .pdf file in the targer folder (for which a valid identifier was found). This option is only available when a folder is targeted, and when the web validation is
                        allowed.
```
### Usage inside a python script:
```python
import pdf2doi
#Try to identify the DOI/identifier of the file 'path/filename.pdf'
result = pdf2doi.pdf2doi('path/filename.pdf',verbose=True)
#the output is a list with three strings
#result = [identifier, type_identifier, file_name]

#Try to identify the DOIs of all pdf files contained in the folder
result  = pdf2doi.pdf2doi('./folder',verbose=True,webvalidation=True) 
#The output is a list containing an element for each .pdf file in the folder,
#and each element has the format [identifier, type_identifier, file_name]

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)