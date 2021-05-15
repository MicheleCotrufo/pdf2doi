# pdf2doi

pdf2doi is a Python library to extract the DOI or other identifiers (e.g. arXiv ID) starting from the .pdf file of a publication (or from a folder containing several .pdf files).
It exploits several methods (see below for detailed description) to find a possible identifier, and it validates any result
via web queries to public archives (e.g. http://dx.doi.org). Additionally, it can **[generate automatically bibtex entries](#generate-list-of-bibtex-entries) for all pdf files in a target folder.**


## Table of Contents
 - [Description](#description)
 - [Installation](#installation)
 - [Usage](#usage)
    * [Usage inside a python script](#usage-inside-a-python-script)
        + [Generate list of bibtex entries](#generate-list-of-bibtex-entries)
        + [Manually associate the correct identifier to a file](#manually-associate-the-correct-identifier-to-a-file)
    * [Command line usage:](#command-line-usage)
        + [Generate list of bibtex entries from command line](#generate-list-of-bibtex-entries-from-command-line)
        + [Manually associate the correct identifier to a file from command line](#manually-associate-the-correct-identifier-to-a-file-from-command-line)
 - [Contributing](#contributing)
 - [License](#license)

## Description
Automatically associating a DOI or other identifiers (e.g. arXiv ID) to a pdf file can be either a very easy or a very difficult
(sometimes nearly impossible) task, depending on how much care was placed in crafting the file. In the simplest case (which typically works with most recent publications)
it is enough to look into the file metadata. For older publications, the identifier is often found within the pdf text and it can be
extracted with the help of regular expressions. In the unluckiest cases, the only method left is to google some details of the publication
(e.g. the title or parts of the text) and hope that a valid identifier is contained in one of the first results.

The ```pdf2doi``` library applies sequentially all these methods (starting from the simplest ones) until a valid identifier is found and validated.
Specifically, for a given .pdf file it will, in order,

1. Look into the metadata of the .pdf file (extracted via the library [PyPDF2](https://github.com/mstamy2/PyPDF2)) and see if any string matches the pattern of 
a DOI or an arXiv ID. Priority is given to metadata which contain the word 'doi' in their label.

2. Check if the file name file contains any sub-string that matches the pattern of 
a DOI or an arXiv ID.

3. Scan the text inside the .pdf file, and check for any string that matches the pattern of 
a DOI or an arXiv ID. The text is extracted with the libraries [PyPDF2](https://github.com/mstamy2/PyPDF2) and [textract](https://github.com/deanmalmgren/textract).

4. Try to find possible titles of the publication. In the current version, possible titles are identified via 
the library [pdftitle](https://github.com/metebalci/pdftitle "pdftitle"), and by the file name. For each possible title a google search 
is performed and the plain text of the first results is scanned for valid identifiers.

5. As a last desperate attempt, the first N=1000 characters of the pdf text are used as a query for
a google search. The plain text of the first results is scanned for valid identifiers.

Any time that a possible identifier is found, it is validated by performing a query to a relevant website (e.g., http://dx.doi.org for DOIs and http://export.arxiv.org for arxiv IDs). 
The validation process returns a valid [bibtex](http://www.bibtex.org/) entry when the identifier is valid. Thus, ```pdf2doi``` can also **[automatically generate bibtex entries for all pdf files in a target folder](#generate-list-of-bibtex-entries-from-command-line)**.

When a valid identifier is found with any method different than the first one, the identifier will also be stored inside the metadata of
the pdf file. In this way, future lookups of this same file will be able to extract the identifier with the 
first method, speeding up the search. This feature can be disabled by the user (in case edits to the pdf file are not desired).

The library is far from being perfect. Often, especially for old publications, none of the currently implemented methods will work. Other times the wrong DOI might be extracted: this can happen, for example, 
if the DOI of another paper is present in the pdf text and it appears before the correct DOI. A quick and dirty solution to this problem is to manually add the correct DOI to the metadata
of the file (with the methods shown [here](#manually-associate-the-correct-identifier-to-a-file) (from python console) or [here](#manually-associate-the-correct-identifier-to-a-file-from-command-line) (from command line). 
In this way, ```pdf2doi``` will always retrieve the correct DOI, which can be useful for the generation of bibtex entries and for when ```pdf2doi```  is used 
for other bibliographic purposes.

Currently, only the format of arXiv identifiers in use after [1 April 2007](https://arxiv.org/help/arxiv_identifier) is supported.

## Installation

Use the package manager pip to install pdf2doi.

```bash
pip install pdf2doi
```

## Usage

pdf2doi can be used either as a [stand-alone application](#command-line-usage) invoked from the command line, or by [importing it in your python project](#usage-inside-a-python-script).


### Usage inside a python script
The function ```pdf2doi.pdf2doi``` is the main point of entry. It can be used to look for the identifier of a pdf file by applying all the available methods. 
The first input argument must be a valid path (either absolute or relative) to a pdf file or to a folder containing pdf files. 
Setting the optional argument ```verbose=True``` will increase the output verbosity, documenting all steps performed by the library. Using as a test the folder [examples](/examples), 

```python
>>> import pdf2doi
>>> results = pdf2doi.pdf2doi('.\examples',verbose=True)
```
generates the output
```
[pdf2doi]: Looking for pdf files in the folder .\examples...
[pdf2doi]: Found 4 pdf files.
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\1-s2.0-0021999186900938-main.pdf
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
[pdf2doi]: Trying to write the identifier '10.1016/0021-9991(86)90093-8' into the metadata of the file '.\examples\1-s2.0-0021999186900938-main.pdf'...
[pdf2doi]: The identifier '10.1016/0021-9991(86)90093-8' was added succesfully to the metadata of the file '.\examples\1-s2.0-0021999186900938-main.pdf' with key '/identifier'...
[pdf2doi]: 10.1016/0021-9991(86)90093-8
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\chaumet_JAP_07.pdf
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
[pdf2doi]: Trying to write the identifier '10.1063/1.2409490' into the metadata of the file '.\examples\chaumet_JAP_07.pdf'...
[pdf2doi]: The identifier '10.1063/1.2409490' was added succesfully to the metadata of the file '.\examples\chaumet_JAP_07.pdf' with key '/identifier'...
[pdf2doi]: 10.1063/1.2409490
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\PhysRevLett.116.061102.pdf
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
[pdf2doi]: Trying to write the identifier '10.1103/PhysRevLett.116.061102' into the metadata of the file '.\examples\PhysRevLett.116.061102.pdf'...
[pdf2doi]: The identifier '10.1103/PhysRevLett.116.061102' was added succesfully to the metadata of the file '.\examples\PhysRevLett.116.061102.pdf' with key '/identifier'...
[pdf2doi]: 10.1103/PhysRevLett.116.061102
[pdf2doi]: ................
[pdf2doi]: Trying to retrieve a DOI/identifier for the file: .\examples\s41586-019-1666-5.pdf
[pdf2doi]: Method #1: Looking for a valid identifier in the document infos...
[pdf2doi]: Validating the possible DOI 10.1038/s41586-019-1666-5 via a query to dx.doi.org...
[pdf2doi]: The DOI 10.1038/s41586-019-1666-5 is validated by dx.doi.org. A bibtex entry was also created.
[pdf2doi]: A valid DOI was found in the document info labelled '/doi'.
[pdf2doi]: 10.1038/s41586-019-1666-5
[pdf2doi]: ................
```
All logging information (i.e. all lines starting with ```[pdf2doi]```) can be suppressed by removing ```verbose=True```. The output of the function
```pdf2doi.pdf2doi``` is a list of dictionaries (or just a single dictionary if a single file was targeted). Each dictionary has the following keys

```
result['identifier'] =      DOI or other identifier (or None if no identifier was found for this file)
result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
result['validation_info'] = Additional info on the paper. If the online validation is enabled, then result['validation_info']
                            will contain a bibtex entry for this paper. Otherwise it will just contain True                         
result['path'] =            path of the pdf file
result['method'] =          method used to find the identifier
```
For example, the DOIs/identifiers of each file can be printed by
```
>>> for result in results:
>>>     print(result['identifier'])
10.1016/0021-9991(86)90093-8
10.1063/1.2409490
10.1103/PhysRevLett.116.061102
10.1038/s41586-019-1666-5
```

Additional optional arguments can be passed to the function ```pdf2doi.pdf2doi``` to control its behaviour, for example to specify if
web-based methods (either to find an identifier and/or to validate it) should not be used.

```python
def pdf2doi(target, verbose=False, websearch=True, webvalidation=True,
            save_identifier_metadata = config.save_identifier_metadata,
            numb_results_google_search=config.numb_results_google_search,
            filename_identifiers = False, filename_bibtex = False):
    '''
    Parameters
    ----------
    target : string
        Relative or absolute path of a .pdf file or a directory containing pdf files
    verbose : boolean, optional
        Increases the output verbosity. The default is False.
    websearch : boolean, optional
        If set false, any method to find an identifier which requires a web search is disabled. The default is True.
    webvalidation : boolean, optional
        If set false, validation of identifiers via internet queries (e.g. to dx.doi.org or export.arxiv.org) is disabled. 
        The default is True.
    save_identifier_metadata : boolean, optional
        If set True, when a valid identifier is found with any method different than the metadata lookup, the identifier
        is also written in the file metadata with key "/identifier" (this will speed up future lookup of thi same file). 
        If set False, this does not happen. The default is True.
    numb_results_google_search : integer, optional
        It sets how many results are considered when performing a google search. The default is config.numb_results_google_search.
    filename_identifiers : string or boolean, optional
        If set equal to a string, all identifiers found in the directory specified by target are saved into a text file 
        with a name specified by filename_identifiers. The default is False.  It is ignored if the input parameter target is a file.
    filename_bibtex : string or boolean, optional
        If set equal to a string, all bibtex entries obtained in the validation process for all pdf files found in the 
        directory specified by target are saved into a file with a name specified by filename_bibtex. The default is False.
        It is ignored if the input parameter target is a file.
    '''
```

By default, everytime that a valid DOI/identifier is found, it is stored in the metadata of the pdf file. In this way, subsequent lookups of the same folder/file will be much faster.
This behaviour can be removed (e.g. if the user does not want or cannot edit the files) by setting the optional argument  ```save_identifier_metadata = False```

#### Generate list of bibtex entries
The online validation of an identifier relies on performing queries to different online archives 
(e.g., http://dx.doi.org for DOIs and http://export.arxiv.org for arxiv IDs). Using data obtained from these queries, a bibtex entry is created
and stored in the 'validation_info' element of the output dictionary. By setting the input argument ```filename_bibtex``` equal to a 
valid filename, the bibtex entries of all files in the target directory will be saved in a file within the same directory. For example,

```python
>>> import pdf2doi
>>> results = pdf2doi.pdf2doi('.\examples', filename_bibtex='bibtex.txt')
```
creates the file [bibtex.txt](/examples/bibtex.txt) in the 'examples' folder. Note that this task can also be done [via command line](#generate-list-of-bibtex-entries-from-command-line), without having to open a python console.

#### Manually associate the correct identifier to a file
Sometimes it is not possible to retrieve a DOI/identifier automatically, or maybe the one that is retrieved is not the correct one. This can be 
a problem when using ```pdf2doi``` to generate the bibtex entries of a bunch of pdf files, or for other bibliographic purposes. This problem can be fixed
by looking for the DOI/identifier manually and add it to the pdf metadata, by using the function ```pdf2doi.add_found_identifier_to_metadata```,
```python
>>> import pdf2doi
>>> pdf2doi.add_found_identifier_to_metadata(path_to_pdf_file, identifier)
```
this creates a new metadata in the pdf file with label '/identifier' and containing the string ```identifier```.   Note that this task can also be done [via command line](#manually-associate-the-correct-identifier-to-a-file-from-command-line), without having to open a python console.

### Command line usage
```pdf2doi``` can also be invoked directly from the command line, without having to open a python console.
The syntax follows closely the one of the ```pdf2doi.pdf2doi``` python function.

The simplest command-line invokation is

```
$ pdf2doi 'path/to/target'
```
where ```target``` is either a valid pdf file or a directory containing pdf files. For example, when targeting the folder [examples](/examples) we get the following output

```
$ pdf2doi ".\examples"
[...same logging information as for the previous example, omitted for brevity...]
DOI             10.1016/0021-9991(86)90093-8             .\examples\1-s2.0-0021999186900938-main.pdf

DOI             10.1063/1.2409490                        .\examples\chaumet_JAP_07.pdf

DOI             10.1103/PhysRevLett.116.061102           .\examples\PhysRevLett.116.061102.pdf

DOI             10.1038/s41586-019-1666-5                .\examples\s41586-019-1666-5.pdf
```

The logging information can be suppressed by adding the optional argument ```-nv``` (no verbose), i.e.
```
$ pdf2doi ".\examples" -nv
```

In the output, the first column specifies the kind of identifier (currently either 'DOI' or 'arxiv'), the second column contains the found DOI/identifier, and the third column contains the file path.

A list of all optional arguments can be generated by ```pdf2doi --h```
```
$ pdf2doi --h
usage: pdf2doi [-h] [-nv] [-nws] [-nwv] [-nostore] [-id IDENTIFIER]
               [-google_results GOOGLE_RESULTS] [-s FILENAME_IDENTIFIERS]
               [-b FILENAME_BIBTEX]
               path

Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a
publications.

positional arguments:
  path                  Relative path of the target pdf file or of the targe
                        folder.

optional arguments:
  -h, --help            show this help message and exit
  -nv, --no_verbose     Decrease verbosity.
  -nws, --no_web_search
                        Disable any method to find identifiers which requires
                        internet searches (e.g. queries to google).
  -nwv, --no_web_validation
                        Disable the online validation of identifiers (e.g.,
                        via queries to http://dx.doi.org/).
  -nostore, --no_store_identifier_metadata
                        By default, anytime an identifier is found it is added
                        to the metadata of the pdf file (if not present yet).
                        By setting this parameter, the identifier is not
                        stored in the file metadata.
  -id IDENTIFIER        Stores the string IDENTIFIER in the metadata of the
                        target pdf file, with key '/identifier'. Note: when this
                        argument is passed, all other arguments (except for
                        the path to the pdf file) are ignored.
  -google_results GOOGLE_RESULTS
                        Set how many results should be considered when doing a
                        google search for the DOI (default=6).
  -s FILENAME_IDENTIFIERS, --save_identifiers_file FILENAME_IDENTIFIERS
                        Save all the identifiers found in the target folder in
                        a text file inside the same folder with name specified
                        by FILENAME_IDENTIFIERS. This option is only
                        available when a folder is targeted.
  -b FILENAME_BIBTEX, --make_bibtex_file FILENAME_BIBTEX
                        Create a text file inside the target directory with
                        name given by FILENAME_BIBTEX containing the bibtex
                        entry of each pdf file in the target folder (if a
                        valid identifier was found). This option is only
                        available when a folder is targeted, and when the web
                        validation is allowed.
```
#### Generate list of bibtex entries from command line

A list of bibtex entries can be generated and saved in a file via the optional argument ```-b```. For example, if the target is the folder 'examples', the command
```
$ pdf2doi ".\examples" -b "bibtex.txt"
```
creates the file [bibtex.txt](/examples/bibtex.txt) inside the same folder. 

#### Manually associate the correct identifier to a file from command line

Similarly to what described [above](#manually-associate-the-correct-identifier-to-a-file), it is possible to associate a (manually found) 
identifier to a pdf file directly from command line, by using the optional argument ```-id```,
```
$ pdf2doi "path\to\pdf" -id "identifier"
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)
