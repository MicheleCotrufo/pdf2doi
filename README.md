# pdf2doi

pdf2doi is a Python library to extract the DOI or other identifiers (e.g. arXiv) from a pdf file of a publication.

## Installation

Use the package manager [pip] to install pdf2doi.

```bash
pip install pdf2doi
```

## Usage

pdf2doi can be used either as a stand-alone application invoked from the command line, or by importing it in your python project.

Example of usage from command line:

```
pdf2doi 'path/filename.pdf'
pdf2doi './folder'
```
```
pdf2doi --h

usage: pdf2doi [-h] [-v] [-nws] [-nwv] [-google_results GOOGLE_RESULTS] filename

Retrieve the DOI of a paper from a PDF file.

positional arguments:
  filename              Relative path of the pdf file or of a folder.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity.
  -nws, --nowebsearch   Disable any DOI retrieval method which requires internet searches (e.g. queries to google).
  -nwv, --nowebvalidation
                        Disable the DOI online validation via queries (e.g., to http://dx.doi.org/).
  -google_results GOOGLE_RESULTS
                        Set how many results should be considered when doing a google search for the DOI (default=6).

```
Example of usage inside a python script:
```python
import pdf2doi
#Try to identify the DOI/identifier of the file 'path/filename.pdf'
result = pdf2doi.pdf2doi('path/filename.pdf',verbose=True)
#the output is a list in the format
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