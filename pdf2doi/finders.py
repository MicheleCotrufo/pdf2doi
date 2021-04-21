"""
This module contains different functions to identify the DOI (or arXiv identifier) of a paper from a PDF file
"""
from PyPDF2 import PdfFileReader
import textract
import requests
import pdftitle
import re
import logging
from googlesearch import search
from . import bibtex_makers
import pdf2doi.config as config
import os

#The list doi_regexp contains several regular expressions used to identify a DOI in a string. They are ordered from stricter to less and less strict
doi_regexp = ['doi[\s\.\:]{0,2}(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n\"<]|$)', # version 0 looks for something like "DOI : 10.xxxxS[end characters] where xxxx=4 digits, S=combination of characters, digits, ., :, -, and / of any length
                                                                            # [end characters] is either a space, newline, " , < or the end of the string. The initial part could be either "DOI : ", "DOI", "DOI:", "DOI.:", ""DOI:." 
                                                                            # and with possible spaces or lower cases.
              '(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n\"<]|$)',                 # in version 1 the requirement of having "DOI : " in the beginning is removed
              '(10\.\d{4}[\:\.\-\/a-z]+[\:\.\-\d]+)(?:[\s\na-z\"<]|$)']     # version 2 is useful for cases in which, in plain texts, the DOI is not followed by a space, newline or special characters,
                                                                            #but is instead followed by other letters. In this case we can still isolate the DOI if we assume that the DOI always ends up with numbers

#Similarly, arxiv_regexp is a list of regular expressions used to identify an arXiv identifier in a string. They are ordered from stricter to less and less strict. Moreover,
#the regexp corresponding to older arXiv notations have less priority.
#NOTE: currently only one regexp is implemented for arxiv. 
arxiv_regexp = ['arxiv[\s]*\:[\s]*(\d{4}\.\d+)(?:v\d+)?(?:[\s\n\"<]|$)',  #version 0 looks for something like "arXiv:YYMM.number(vn)" 
                                                                            #where YYMM are 4 digits, numbers are up to 5 digits and (vn) is
                                                                            #an additional optional term specifying the version. n is an integer starting from 1
                                                                            #This is the official format for Arxiv indentifier starting from 1 April 2007
                '(\d{4}\.\d+)(?:v\d+)?(?:\.pdf)'] 

def validate(identifier,what='doi'):
    """
    Check that an identifier is a valid identifier by using a regular expression.
    If config.check_online_to_validate, it also checks that the identifier is actually associate to a paper via 
    a query to the proper website (e.g. http://dx.doi.org/ for DOIs).

    Parameters
    ----------
    identifier : string
        The identifier (e.g. doi or arXiv ID) to validate.
    what : string, optional. Possible values = 'doi' (default), 'arxiv'
        Specifies the kind of identifier to be validated.
    Returns
    -------
    result : It is either boolean (True if identifier is valid, False if is not valid) or a string
        If config.check_online_to_validate is set to true, the validation process also generate a valid bibtex entry, which is 
        returned a string in result
    """  
    if not identifier:
        return None
    if what=='doi':
        if re.match(doi_regexp[1],identifier,re.I):
            if config.check_online_to_validate:
                logging.info(f"Validating the possible DOI {identifier} via a query to dx.doi.org...")
                result = bibtex_makers.doi2bib(identifier)
                if result==-1:
                    logging.error(f"Some error occured during connection to dx.doi.org.")
                    return None
                if result:
                    logging.info(f"The DOI {identifier} is validated by dx.doi.org. A bibtex entry was also created.")
                    return result
                else:
                    logging.info(f"The DOI {identifier} is not valid according to dx.doi.org.")
                    return False
            else:
                logging.info(f"(web validation is deactivated. Set webvalidation = True in order to validate a potential DOI on dx.doi.org).")
                return True
        else: return False

    elif what=='arxiv':
        if re.match(r'(\d{4}\.\d+(?:v\d+)?)',identifier,re.I):
            if config.check_online_to_validate:
                logging.info(f"Validating the possible arxiv ID {identifier} via a query to export.arxiv.org...")
                result = bibtex_makers.arxiv2bib(identifier)
                if result==-1:
                    logging.error(f"Some error occured during connection to export.arxiv.org.")
                    return None
                if result:
                    logging.info(f"The Arxiv ID {identifier} is validated by export.arxiv.org. A bibtex entry was also created.")
                    return result
                else:
                    logging.info(f"The Arxiv ID {identifier} is not valid according to export.arxiv.org.")
                    return False
            else:
                logging.warning(f"(web validation is deactivated. Set webvalidation = True in order to validate a potential arxiv ID on export.arxiv.org).")
                return True
        else: return False

    return False


def extract_arxivID_from_text(text,version=0):   
    """
    It looks for an arxiv ID in the input argument 'text', by using the regexp specified by arxiv_regexp[version],
    where arxiv_regexp is a list of strings defined in this file and 'version' is an input value.

    Parameters
    ----------
    text : string
        Text to analyse
    version : integer, optional
        Numerical value defined between 0 and len(arxiv_regexp)-1. It specifies which element of the list
        arxiv_regexp is used for the regular expression

    Returns
    -------
    arxivID : string or None
        It returns the arxiv ID if any was found, or None
    """                                               
    regexDOI = re.search(arxiv_regexp[version] ,text,re.I)
    if regexDOI:
        print(regexDOI.group(1))
        return regexDOI.group(1)
    return None

def extract_doi_from_text(text,version=0):
    """
    It looks for a DOI in the input argument 'text', by using the regexp specified by doi_regexp[version],
    where doi_regexp is a list of strings defined in this file and 'version' is an input value.

    Parameters
    ----------
    text : string
        Text to analyse
    version : integer, optional
        Numerical value defined between 0 and len(doi_regexp)-1. It specifies which element of the list
        doi_regexp is used for the regular expression

    Returns
    -------
    doi : string or None
        It returns the doi if any was found, or None

    """    
    regexDOI = re.search(doi_regexp[version],text,re.I)
    if regexDOI:
        return regexDOI.group(1)
    return None

def find_identifier_in_google_search(query,func_validate,numb_results=10):
    logging.info(f"Performing google search with key \'" + query + "\'")
    i=1
    for url in search(query, stop=numb_results):
        logging.info(f"Looking for a valid identifier in the search result #{str(i)} : {url}")
        response = requests.get(url)
        text = response.text
        identifier,desc,info = find_identifier_in_text(text,func_validate)
        if identifier: 
            logging.info(f"A valid {desc} was found in the document text.")
            return identifier,desc,info
        i=i+1
    return None, None, None

def find_identifier_in_text(texts,func_validate):
    """
    Given any string (or list of strings), it looks for any pattern which matches a valid identifier (e.g. a DOi or an arXiv ID). 
    If a list of string is passed as an argument, they are checked in the order in which they appear in the list, 
    and the function stops as soon as a valid identifier is found.

    Parameters
    ----------
    texts : string or a list of strings
       text to analyse.
    func_validate : 
        
    Returns
    -------
    doi
        A valid DOI if any is found, or None if no DOI was found.
    desc
        Description of what was found (e.g. 'doi,''arxiv')

    """
    if not isinstance(texts,list): texts = [texts]
    
    for text in texts:
        #First we look for DOI
        for v in range(len(doi_regexp)):
            doi = extract_doi_from_text(text,version=v)
            validation = func_validate(doi,'doi')
            if validation: 
                return doi, 'DOI', validation
            
        #Then we look for an Arxiv ID
        for v in range(len(arxiv_regexp)):
            arxivID = extract_arxivID_from_text(text,version=v)
            validation = func_validate(arxivID,'arxiv')
            if validation:
                return arxivID,'arxiv ID', validation
    return None, None, None


def get_pdf_info(path):
    """
    Given a valid path to a pdf file, it return a dictionary of info. 
    Currently, it uses PyPDF to extract the info.
    
    Parameters
    ----------
    path : a valid path to a pdf file
    
    Returns
    -------
    info: dictionary
    """
    try:
        file = open(path, 'rb') 
    except (FileNotFoundError, IOError):
        logging.error("File not found.")
        return None
    try:
        pdf = PdfFileReader(path,strict=False)
    except:
        logging.error("It was not possible to open the file with PyPDF2. Is this a valid pdf file?")
        return None
    info = pdf.getDocumentInfo()
    return info
    
def find_possible_titles(path):
    """
    Given a valid path to a pdf file, it tries to extract a list of possible titles. 
    In the current implementation it looks for titles by 1) looking for the outcome of pdftitle library, 
    2) looking in the dictionary returned by the PyPDF library and 3) looking in the filename.

    Parameters
    ----------
    path : a valid path to a pdf file
    
    Returns
    -------
    titles : list of strings
        Possible titles of the paper.
    """
    titles = []
    # (1)    
    try:
        title = pdftitle.get_title_from_file(path)
    except:
        title = ''
    if len(title)>5:#This is to check that the title found is neither empty nor just few characters
        titles.append(title)  
        
    # (2)
    info = get_pdf_info(path)
    if not(info): return None
    
    for key, value in info.items():
        if 'title' in key.lower():
            if isinstance(value,str) and len(value)>5: #This is to check that the title found is neither empty nor just few characters
                titles.append(value)         
    # (3)
    title = os.path.basename(path)
    if len(title)>5:#This is to check that the title found is neither empty nor just few characters
        titles.append(title)
        
    return titles
        
def get_pdf_text(path,reader):
    """
    Given a valid path to a pdf file, it returns the text of the pdf file extracted with the library 
    specified in the 'reader' input variable.

    Parameters
    ----------
    path : a valid path to a pdf file
    reader : It specifies which library is used to extract the text from the pdf.
        The supported values are either 'pypdf' (uses the PyPDF2 module) or 'textract' (uses the 'textract' module)
    Returns
    -------
    text : list of strings
    """
    text =[]
    if reader == 'pdfminer':
        text = high_level.extract_text(path, "", 0)
    if reader == 'pypdf':
        with open(path, "rb") as f:
            try:
                pdf = PdfFileReader(f,strict=False)
            except:
                logging.error("The input argument 'pdf' must be a valid path to a pdf file.")
                return None
            number_of_pages = pdf.getNumPages()
            for i in range(number_of_pages):
                try:
                    text.append( (pdf.getPage(i)).extractText())
                except Exception as e:
                    logging.error("An error occured while loading the document text with PyPDF2. The pdf version might be not supported.")
                    break 
    if reader == 'textract':
        try:
            text = [textract.process(path).decode('utf-8')]
        except:
            try:
                text = [textract.process(path)]
            except:   
                logging.error("An error occured while loading the document text with textract. The pdf version might be not supported.")
    return text

###########################################################################################################
###########################################################################################################
###########################################################################################################




def find_identifier(path,method,func_validate=validate,**kwargs):
    """ Tries to find an identifier (e.g. DOI, arxiv ID,...) for the pdf file identified by the input
    argument 'path', by using the method specified by input argument 'method'. Any found identifier is validated
    by using the function func_validate.

    Parameters
    ----------
    path : string
        A valid path to a pdf file
    method : string
        Method to be used to look for an identifier. The possible values are specified by the keys of 
        the dictionary finder_methods.
    func_validate : function, optional, the default value is the validate() function defined in this module
        The function func_validate must take one string argument and return True/False.
        If func_validate is specified, everytime that a possible identifier is found the value 
        returned by func_validate is used to check if identifier is valid.    
    kwargs : 
        additional input parameters specific to the method chosen
        
    Returns
    -------
    result : dictionary
        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper. If config.check_online_to_validate = True, then result['validation_info']
                                    will typically contain a bibtex entry for this paper. Otherwise it will just contain True                         
        result['path'] = path of the pdf file
        result['method'] = method used to find the identifier

    """
    if not method in  finder_methods.keys():
        raise ValueError("The input variable method is not valid. Possible values = \'" + "\',\'".join(finder_methods.keys())+"\'")
    if not callable(func_validate):  func_validate = lambda x : x

    identifier, desc, info = finder_methods[method](path,func_validate,**kwargs)
    
    result = {'identifier':identifier,'identifier_type':desc,'validation_info':info,
              'path':path, 'method':method}
    return result

def find_identifier_by_googling_title(path, func_validate, numb_results=config.numb_results_google_search):
    
    logging.info("Looking for a possible publication title in the document infos...")
    titles = find_possible_titles(path)

    if titles:
        if config.websearch==False:
            logging.warning("Possible titles of the paper were found, but the web-search method is currently disabled by the user. Enable it in order to perform a qoogle query.")
        else:
            for title in titles:
                logging.info(f"A possible title was found: \"{title}\"")
                logging.info(f"Doing a google search, looking at the first {config.numb_results_google_search} results...")
                identifier,desc,info = find_identifier_in_google_search(title,func_validate,numb_results)
                if identifier:
                    return identifier,desc,info
            logging.info("None of the search results contained a valid identifier.")     
            return None, None, None
    else:
        logging.error("It was not possible to find a title (for a google lookup) for this file.")
        return None, None, None
 

def find_identifier_in_pdf_info(path,func_validate,keysToCheckFirst=[]):
    """ 
    Try to find a valid DOI in the values of the 'document information' dictionary. If a list of string is specified via the optional
    input parameter 'keysToCheckFirst', then the corresponding elements of the dictionary (assuming that the key exists) are given
    priority.

    Parameters
    ----------
    path : a valid path to a pdf file
    keysToCheckFirst : list, optional
        A list of strings. If specified, element of the 'document information' dictionary with these keys (assuming that 
       they exist) are given priority in the DOI search (following the order they appear in this list)
    func_validate : function
        The function func_validate must take one string argument and return True/False.
        Everytime that a possible identifier is found the value returned by func_validate is used to check if identifier is valid.
    Returns
    -------
    result : dictionary with identifier and other info (see above) 
    """
    
    logging.info("Looking for a valid identifier in the document infos...")
    pdfinfo = get_pdf_info(path)
    identifier, desc, info = None, None, None
    if pdfinfo:
        Keys = keysToCheckFirst + list(pdfinfo.keys()) #Quick way to create a list of keys where the elements of keysToCheckFirst appear first. 
                                            #Some elements of keysToCheckFirst might be duplicated in 'Keys', but this is not a problem
                                            #because the corresponding element in the pdfinfo dictionary is eliminated after being checked
        for key in Keys:
            if key in pdfinfo.keys():
                identifier,desc,info = find_identifier_in_text(pdfinfo[key],func_validate)
                if identifier: 
                    logging.info(f"A valid {desc} was found in the document info labelled \'{key}\'.")
                    break
                del pdfinfo[key]
    if identifier:
        return identifier,desc,info
    else:
        logging.info("Could not find a valid identifier in the document info.")
        return None, None, None
    
def find_identifier_in_filename(path, func_validate):
    """ 
    Parameters
    ----------
    path : a valid path to a pdf file
    func_validate : function
        The function func_validate must take one string argument and return True/False.
        Everytime that a possible identifier is found the value returned by func_validate is used to check if identifier is valid.
    Returns
    -------
    result : dictionary with identifier and other info (see above)
    """
    logging.info("Looking for a valid identifier in the file name...")
    text = os.path.basename(path)
    identifier,desc,info = find_identifier_in_text([text],func_validate)
    if identifier: 
        logging.info(f"A valid {desc} was found in the file name.")
        return identifier,desc,info
    else:
        logging.info("Could not find a valid identifier in the file name.")
        return None, None, None


def find_identifier_in_pdf_text(path, func_validate, reader = 'pypdf' ):
    """ Try to find a valid identifier in the plain text of the pdf file. The text is extracted via the function
    get_pdf_text which uses the library specified in the input variable 'reader' to produce a string or list of strings.

    Parameters
    ----------
    path : a valid path to a pdf file
    reader : string, optional
        It specifies which library is used to extract the text from the pdf.
        The supported values are either 'pypdf' (uses the PyPDF2 module) or 'textract' (uses the 'textract' module)
    func_validate : function
        The function func_validate must take one string argument and return True/False.
        Everytime that a possible identifier is found the value returned by func_validate is used to check if identifier is valid.
    Returns
    -------
    result : dictionary with identifier and other info (see above)
    """
    logging.info(f"Looking for a valid identifier in the document text...")
    for reader in reader_libraries:
        logging.info(f"Extracting text with the library {reader}...")
        texts = get_pdf_text(path,reader.lower())
        
        if not isinstance(texts,list):
            texts = [texts]
        identifier,desc,info = find_identifier_in_text(texts,func_validate)
        if identifier: 
            logging.info(f"A valid {desc} was found in the document text.")
            return identifier,desc,info
        else:
            logging.info(f"Could not find a valid identifier in the document text extracted by {reader}.")
    logging.info(f"Could not find a valid identifier in the document text.")
    return None, None, None
        


#The dictionary finder_methods list all the methods currently implemented to find an identifier.
#Each method is associated to a function.
#The keys of this dictionary corresponds to the possible values of the input argument 'method' 
#passed the function find_identifier
finder_methods = {
                    "document_infos"    : find_identifier_in_pdf_info,
                    "document_text"     : find_identifier_in_pdf_text,
                    "filename"          : find_identifier_in_filename,
                    "title_google"      : find_identifier_by_googling_title
                    }

reader_libraries = ['PyPdf','textract']
