# pdf2doi

pdf2doi is a Python library to extract the DOI or other identifiers (e.g. arXiv ID) starting from the .pdf file of a publication (or from a folder containing several .pdf files).
It exploits several methods (see below for detailed description) to find a possible identifier, and it validates any result
via web queries to public archives (e.g. http://dx.doi.org). Additionally, it can be used to generate automatically bibtex entries for all pdf files in a folder.
Currently, only the format of arXiv identifiers in use after [1 April 2007](https://arxiv.org/help/arxiv_identifier) is supported.


## Description
Automatically associating a DOI or other identifiers (e.g. arXiv ID) to a pdf file can be either a very easy or a very difficult
(sometimes nearly impossible) task, depending on how much care was placed in crafting the file. In the simplest case (which typically applies to most recent publications)
it is enough to look into the file metadata. For older publications, the identifier is often found within the pdf text and it can be
extracted with the help of regular expressions. In the unluckiest cases, the only method left is to google some details of the publication
(e.g. the title or parts of the text) and hope that a valid identifier is contained in one of the first results.

The ```pdf2doi``` library applies sequentially all these methods (starting from the simplest ones) until a valid identifier is found and validated.
Specifically, for a given .pdf file it will, in order,

1. Look into the metadata of the .pdf file (extracted via the library [PyPDF2](https://github.com/mstamy2/PyPDF2)) and see if any string matches the pattern of 
a DOI or an arXiv ID. Priority is given to the metadata which contain the word 'doi' in their label.

2. Check if the name of the pdf file contains any sub-string that matches the pattern of 
a DOI or an arXiv ID.

3. Scan the text inside the .pdf file, and check for any string that matches the pattern of 
a DOI or an arXiv ID. The text is extracted with the libraries [PyPDF2](https://github.com/mstamy2/PyPDF2) and [textract](https://github.com/deanmalmgren/textract).

4. Try to find possible titles of the publication. In the current version, possible titles are identified via 
the library [pdftitle](https://github.com/metebalci/pdftitle "pdftitle"), and by the file name. For each possible title a google search 
is performed and the plain text of the first results is scanned for valid identifiers.

5. As a last desperate attempt, the first N=1000 characters of the pdf text are used as a query for
a google search (the value of N can be set by the variable config.N_characters_in_pdf). The plain text of the first results is scanned for valid identifiers.

Any time that a possible identifier is found, it is validated by performing a query to a relevant website (e.g., http://dx.doi.org for DOIs and http://export.arxiv.org for arxiv IDs). 
The validation process returns a valid [bibtex](http://www.bibtex.org/) entry. Thus, ```pdf2doi``` can be also used to automatically generate bibtex entries for all pdf files in a target folder (see below for details).

When a valid identifier is found with any method different than the first one, the identifier is also stored inside the metadata of
the pdf file with key='/identifier'. In this way, future lookups of this file will be able to extract the identifier with the 
first method, speeding up the search. This feature can be disabled by the user (in case edits to the pdf file are not desired).

The library is far from being perfect. Often, especially for old publications, none of the currently implemented method will work. Other times the wrong DOI might be extracted: this can happen, for example, 
if the DOI of another paper is present in the pdf text and it appears before the correct DOI. A quick and dirty solution to this problem is to manually add the correct DOI to the the metadata
of the file (with the method shown below). In this way, ```pdf2doi``` will always retrieve the correct DOI, which is useful for the generation of bibtex entries and for when ```pdf2doi```  is used 
for other bibliographic purposes.

## Installation

Use the package manager pip to install pdf2doi.

```bash
pip install pdf2doi
```

## Usage

pdf2doi can be used either as a stand-alone application invoked from the command line, or by importing it in your python project.


### Command line usage:
The simplest way to use ```pdf2doi``` via command line is to just type

```
>>pdf2doi 'path/to/target'
```
where target is either a valid pdf file or a directory containing pdf files.


```
>>pdf2doi "C:\Users\miche\Desktop\examples"
[pdf2doi]: Looking for pdf files in the folder C:\Users\miche\Desktop\examples...
[pdf2doi]: Found 5 pdf files.
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: C:\Users\miche\Desktop\examples\1-s2.0-0021999186900938-main.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Could not find a valid identifier in the document text extracted by PyPdf.
[pdf2doi]: Extracting text with the library textract...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Could not find a valid identifier in the document text extracted by textract.
[pdf2doi]: Could not find a valid identifier in the document text.
[pdf2doi]: Method #4: Looking for possible publication titles...
[pdf2doi]: Found 3 possible title(s).
[pdf2doi]: Doing a google search for "An Efficient Numerical Evaluation of the Green’s Function for the Helmholtz Operator on Periodic Structures",
[pdf2doi]: looking at the first 6 results...
[pdf2doi]: Performing google search with key "An Efficient Numerical Evaluation of the Green’s Function for the Helmholtz Operator on Periodic Str ...[query too long, the remaining part is suppressed in the logging]"
[pdf2doi]: Looking for a valid identifier in the search result #1 : https://www.sciencedirect.com/science/article/pii/0021999186900938
[pdf2doi]: Validating the possible DOI 10.1016/0021-9991(86)90093-8 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1016/0021-9991(86)90093-8 is validated by dx.doi.org. A bibtex entry was also created.
[pdf2doi]: A valid DOI was found with this google search.
[pdf2doi]: Trying to write the identifier '10.1016/0021-9991(86)90093-8' into the metadata of the file 'C:\Users\miche\Desktop\examples\1-s2.0-0021999186900938-main.pdf'...
[pdf2doi]: The identifier '10.1016/0021-9991(86)90093-8' was added succesfully to the metadata of the file 'C:\Users\miche\Desktop\examples\1-s2.0-0021999186900938-main.pdf' with key '/identifier'...
[pdf2doi]: 10.1016/0021-9991(86)90093-8
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: C:\Users\miche\Desktop\examples\chaumet_JAP_07.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Validating the possible DOI 10.1063/1.2409490I.INTRODUCTION via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1063/1.2409490I.INTRODUCTION is not valid according to dx.doi.org.
[pdf2doi]: Validating the possible DOI 10.1063/1.2409490I.INTRODUCTION via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1063/1.2409490I.INTRODUCTION is not valid according to dx.doi.org.
[pdf2doi]: Validating the possible DOI 10.1063/1.2409490 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1063/1.2409490 is validated by dx.doi.org. A bibtex entry was also created.
[pdf2doi]: A valid DOI was found in the document text.
[pdf2doi]: Trying to write the identifier '10.1063/1.2409490' into the metadata of the file 'C:\Users\miche\Desktop\examples\chaumet_JAP_07.pdf'...
[pdf2doi]: The identifier '10.1063/1.2409490' was added succesfully to the metadata of the file 'C:\Users\miche\Desktop\examples\chaumet_JAP_07.pdf' with key '/identifier'...
[pdf2doi]: 10.1063/1.2409490
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: C:\Users\miche\Desktop\examples\PhysRevLett.116.061102.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Validating the possible DOI 10.1103/PhysRevLett.116.061102 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1103/PhysRevLett.116.061102 is validated by dx.doi.org. A bibtex entry was also created.
[pdf2doi]: A valid DOI was found in the document text.
[pdf2doi]: Trying to write the identifier '10.1103/PhysRevLett.116.061102' into the metadata of the file 'C:\Users\miche\Desktop\examples\PhysRevLett.116.061102.pdf'...
[pdf2doi]: The identifier '10.1103/PhysRevLett.116.061102' was added succesfully to the metadata of the file 'C:\Users\miche\Desktop\examples\PhysRevLett.116.061102.pdf' with key '/identifier'...
[pdf2doi]: 10.1103/PhysRevLett.116.061102
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: C:\Users\miche\Desktop\examples\PhysRevLett.76.1055.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Could not find a valid identifier in the document info.
[pdf2doi]: Method #2: Looking for a valid identifier in the file name...
[pdf2doi]: Could not find a valid identifier in the file name.
[pdf2doi]: Method #3: Looking for a valid identifier in the document text...
[pdf2doi]: Extracting text with the library PyPdf...
[pdf2doi]: Error from PyPDF2: ord() expected string of length 1, but int found
[pdf2doi]: An error occured while loading the document text with PyPDF2. The pdf version might be not supported.
[pdf2doi]: Extracting text with the library textract...
[pdf2doi]: Text extracted succesfully. Looking for an identifier in the text...
[pdf2doi]: Could not find a valid identifier in the document text extracted by textract.
[pdf2doi]: Could not find a valid identifier in the document text.
[pdf2doi]: Method #4: Looking for possible publication titles...
[pdf2doi]: Found 1 possible title(s).
[pdf2doi]: Doing a google search for "Arbitrary Control of a Quantum Electromagnetic Field",
[pdf2doi]: looking at the first 6 results...
[pdf2doi]: Performing google search with key "Arbitrary Control of a Quantum Electromagnetic Field"
[pdf2doi]: Looking for a valid identifier in the search result #1 : https://link.aps.org/doi/10.1103/PhysRevLett.76.1055
[pdf2doi]: Validating the possible DOI 10.1103/PhysRevLett.76.1055 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1103/PhysRevLett.76.1055 is validated by dx.doi.org. A bibtex entry was also created.
[pdf2doi]: A valid DOI was found with this google search.
[pdf2doi]: Trying to write the identifier '10.1103/PhysRevLett.76.1055' into the metadata of the file 'C:\Users\miche\Desktop\examples\PhysRevLett.76.1055.pdf'...
[pdf2doi]: The identifier '10.1103/PhysRevLett.76.1055' was added succesfully to the metadata of the file 'C:\Users\miche\Desktop\examples\PhysRevLett.76.1055.pdf' with key '/identifier'...
[pdf2doi]: 10.1103/PhysRevLett.76.1055
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: C:\Users\miche\Desktop\examples\s41586-019-1666-5.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Validating the possible DOI 10.1038/s41586-019-1666-5 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1038/s41586-019-1666-5 is validated by dx.doi.org. A bibtex entry was also created.
[pdf2doi]: A valid DOI was found in the document info labelled '/doi'.
[pdf2doi]: 10.1038/s41586-019-1666-5
[pdf2doi]: ................
DOI             10.1016/0021-9991(86)90093-8             C:\Users\miche\Desktop\examples\1-s2.0-0021999186900938-main.pdf

DOI             10.1063/1.2409490                        C:\Users\miche\Desktop\examples\chaumet_JAP_07.pdf

DOI             10.1103/PhysRevLett.116.061102           C:\Users\miche\Desktop\examples\PhysRevLett.116.061102.pdf

DOI             10.1103/PhysRevLett.76.1055              C:\Users\miche\Desktop\examples\PhysRevLett.76.1055.pdf

DOI             10.1038/s41586-019-1666-5                C:\Users\miche\Desktop\examples\s41586-019-1666-5.pdf

```

The library can also be used directly from the command line, without having to open a python console.

- Find and print the identifier of a single paper, outputting all logs:


- Find and print the identifiers of all pdf files contanined in a folder:
```
>>pdf2doi '.\examples\' --no_verbose
```

- Find the identifiers of all pdf files contanined in a folder and create a text file with all the bibtex entries:
```
>>pdf2doi '.\examples\' -b 'bibtex.txt' --no_verbose
```

The syntax for the command-line invokation follows closely the arguments that can be passed to the pdf2doi python function,

```
>> pdf2doi --h
usage: pdf2doi [-h] [-nv] [-nws] [-nwv] [-nsim]
               [-google_results GOOGLE_RESULTS] [-s [FILENAME_IDENTIFIERS]]
               [-b [FILENAME_BIBTEX]]
               path

Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a
publications.

positional arguments:
  path                  Relative path of the pdf file or of a folder.

optional arguments:
  -h, --help            show this help message and exit
  -nv, --no_verbose     Decrease verbosity.
  -nws, --no_web_search
                        Disable any method to find identifiers which requires
                        internet searches (e.g. queries to google).
  -nwv, --no_web_validation
                        Disable the online validation of identifiers (e.g.,
                        via queries to http://dx.doi.org/).
  -nsim, --no_store_identifier_metadata
                        By default, anytime an identifier is found it is added
                        to the metadata of the pdf file (if not present yet).
                        By setting this parameter, the identifier is not
                        stored in the file metadata.
  -google_results GOOGLE_RESULTS
                        Set how many results should be considered when doing a
                        google search for the DOI (default=6).
  -s FILENAME_IDENTIFIERS, --save_identifiers_file FILENAME_IDENTIFIERS
                        Save all the identifiers found in the target folder in
                        a text file inside the same folder with name specified
                        by FILENAME_IDENTIFIERS (only available when a folder
                        is targeted).
  -b FILENAME_BIBTEX, --make_bibtex_file FILENAME_BIBTEX
                        Create a text file inside the target directory with
                        name given by FILENAME_BIBTEX containing the bibtex
                        entry of each pdf file in the target folder (if a
                        valid identifier was found). This option is only
                        available when a folder is targeted, and when the web
                        validation is allowed.
```

### Usage inside a python script:
The function ```pdf2doi``` can be used to look for the identifier of a pdf file by applying all the available methods. Setting ```verbose=True``` will increase the output verbosity, documenting all steps performed.
```python
import pdf2doi
result = pdf2doi.pdf2doi('.\examples\PhysRevLett.116.061102.pdf',verbose=True)
print('\n')
print(result['identifier'])
print(result['identifier_type'])
print(result['method'])
```
 The previous code produces the output
```
................
File: .\examples\PhysRevLett.116.061102.pdf
Looking for a valid identifier in the document infos...
Could not find a valid identifier in the document info.
Looking for a valid identifier in the file name...
Could not find a valid identifier in the file name.
Looking for a valid identifier in the document text...
Extracting text with the library PyPdf...
Validating the possible DOI 10.1103/PhysRevLett.116.061102 via a query to dx.doi.org...
The DOI 10.1103/PhysRevLett.116.061102 is validated by dx.doi.org. A bibtex entry was also created.
A valid DOI was found in the document text.

10.1103/PhysRevLett.116.061102
DOI
document_text
```

The output variable ```result``` is a dictionary containing the identifier and other relevant information,
```
result['identifier'] =      DOI or other identifier (or None if nothing is found)
result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
result['validation_info'] = Additional info on the paper. If the online validation is enabled, then result['validation_info']
                            will typically contain a bibtex entry for this paper. Otherwise it will just contain True                         
result['path'] =            path of the pdf file
result['method'] =          method used to find the identifier
```

The first argument passed to the function ```pdf2doi``` can also be a directory. In this case the function will 
look for all valid pdf files inside the directory, try to find a valid identifier for each of them,
and return a list of dictionaries.

For example, the code 
```python
import pdf2doi
results = pdf2doi.pdf2doi('.\examples')
for result in results:
    print(result['identifier'])
```
produces the output
```
10.1103/PhysRevLett.116.061102
10.1103/PhysRevLett.76.1055
10.1038/s41586-019-1666-5
```
Additional arguments can be passed to the function ```pdf2doi``` to control its behaviour, for example to specify if
web-based methods (either to find an identifier and/or to validate it) should not be used.

```
def pdf2doi(target, verbose=False, websearch=True, webvalidation=True,
            save_identifier_metadata = config.save_identifier_metadata,
            numb_results_google_search=config.numb_results_google_search,
            filename_identifiers = False, filename_bibtex = False):
    '''
    Parameters
    ----------
    target : string
        Relative or absolute path of the target .pdf file or directory
    verbose : boolean, optional
        Increases the output verbosity. The default is False.
    websearch : boolean, optional
        If set false, any method to find an identifier which requires a web search is disabled. The default is True.
    webvalidation : boolean, optional
        If set false, validation of identifier via internet queries (e.g. to dx.doi.org or export.arxiv.org) is disabled. 
        The default is True.
    save_identifier_metadata : boolean, optional
        If set True, when a valid identifier is found with any method different than the metadata lookup, the identifier
        is also written in the file metadata with key "/identifier". If set False, this does not happen. The default
        is True.
    numb_results_google_search : integer, optional
        It sets how many results are considered when performing a google search. The default is config.numb_results_google_search.
    filename_identifiers : string or boolean, optional
        If is set equal to a string, all identifiers found in the directory specified by target are saved into a text file 
        with a path specified by filename_identifiers. The default is False.
        It is ignored if the input parameter target is a file.
    filename_bibtex : string or boolean, optional
        If is set equal to a string, all bibtex entries obtained in the validation process for the pdf files found in the 
        directory specified by target are saved into a text file with a path specified by filename_bibtex. 
        The default is False.
        It is ignored if the input parameter target is a file.

    Returns
    -------
    results, dictionary or list of dictionaries (or None if an error occured)
        The output is a single dictionary if target is a file, or a list of dictionaries if target is a directory, 
        each element of the list describing one file. Each dictionary has the following keys
        
        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper. If config.check_online_to_validate = True, then result['validation_info']
                                    will typically contain a bibtex entry for this paper. Otherwise it will just contain True                         
        result['path'] = path of the pdf file
        result['method'] = method used to find the identifier

    ''' 
```

The online validation of an identifier relies on performing queries to different online archives 
(e.g. dx.doi.org for DOIs or export.arxiv.org for arXiv identifiers). Using data obtained from these queries, a bibtex entry is created
and stored in the 'validation_info' element of the output dictionary. By setting the input argument ```filename_bibtex``` equal to a 
valid filename, the bibtex entries of all papers in the target directory will be saved in a file within the same directory.

For example,
```python
import pdf2doi
results = pdf2doi.pdf2doi('.\examples',filename_bibtex='bibtex.txt')
```
creates the file [bibtex.txt](/examples/bibtex.txt) in the 'examples' folder.



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)