"""
This module contains different functions to identify the DOI (or arXiv identifier) of a paper from a PDF file
"""
from PyPDF2 import PdfFileReader
import textract
import requests
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
arxiv_regexp = ['arxiv[\s]*\:[\s]*(\d{4}\.\d+(?:v\d+)?)(?:[\s\n\"<]|$)',  #version 0 looks for something like "arXiv:YYMM.number(vn)" 
                                                                            #where YYMM are 4 digits, numbers are up to 5 digits and (vn) is
                                                                            #an additional optional term specifying the version. n is an integer starting from 1
                                                                            #This is the official format for Arxiv indentifier starting from 1 April 2007
                '(\d{4}\.\d+(?:v\d+)?)(?:\.pdf)'] 


def validate(doi,what='doi'):
    """
    Check that doi is a valid DOI by using a regular expression.
    If check_also_online=true, it also checks that the doi is actually associate to a paper via a query to http://dx.doi.org/
    """
    if not doi:
        return None
    #print(config.check_online_to_validate)
    if what=='doi':
        if re.match(r'(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n]|$)',doi,re.I):
            if config.check_online_to_validate:
                logging.info(f"Validating the possible DOI {doi} via a query to dx.doi.org...")
                result = bibtex_makers.doi2bib(doi)
                if (result.lower().find( "DOI Not Found".lower() ))==-1:
                    logging.info(f"DOI validated.")
                    return True
                else:
                    logging.info(f"DOI not valid.")
                    return False
            else:
                logging.info(f"(web validation is deactivated. Set webvalidation = True in order to validate a potential DOI on dx.doi.org).")
                return True
    elif what=='arxiv':
        if re.match(r'(\d{4}\.\d+(?:v\d+)?)',doi,re.I):
            if config.check_online_to_validate:
                logging.info(f"Validating the possible arxiv ID {doi} via a query to export.arxiv.org...")
                result = bibtex_makers.arxiv2bib(doi)
                if result:
                    return True
                else:
                    return False
            else:
                logging.warning(f"(web validation is deactivated. Set webvalidation = True in order to validate a potential arxiv ID on export.arxiv.org).")
                return True
    return False


def extract_arxivID_from_text(text,version=0):   
    """
    It looks for an arxiv ID in the input argument 'text', by using the regexp specified by 
    the input variable 'version'
    
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
        return regexDOI.group(1)
    return None

def extract_doi_from_text(text,version=0):
    """
    It looks for an DOI in the input argument 'text', by using the regexp specified by 
    the input variable 'version'
    
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

def find_doi_in_text(texts,func_validate_doi):
    """
    Given any string (or list of strings), it looks for any pattern which matches either a DOI or an arxiv ID. 
    If a list of string is passed as an argument,they are checked in the order in which they appear in the list, 
    and the function stops as soon as a valid DOI is identified.

    Parameters
    ----------
    texts : string or a list of strings
       text to analyse.
    func_validate_doi : function
        The function func_validate_doi must take one argument and return True/False.
        Everytime that a possible DOI is identified the boolean value returned by func_validate_doi(DOI) is used to check if DOI is valid.

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
            if func_validate_doi(doi,'doi'): 
                return doi, 'doi'
            
        #Then we look for an Arxiv ID
        for v in range(len(arxiv_regexp)):
            arxivID = extract_arxivID_from_text(text,version=v)
            if func_validate_doi(arxivID,'arxiv'):
                return arxivID,'arxiv' 
    return None, None


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
    Given a valid path to a pdf file, it tries to extract a list of possible titles. In the current implementation 
    it looks for titles only in the dictionary returned by the PyPDF library.

    Parameters
    ----------
    path : a valid path to a pdf file
    
    Returns
    -------
    titles : list of strings
        Possible titles of the paper, found either in the info dictionary or in the text (the second one is still to be implemented)
    """
    info = get_pdf_info(path)
    if not(info): return None
    titles = []
    for key, value in info.items():
        if 'title' in key.lower():
            titles.append(value)
    return titles
        
def get_pdf_text(path,reader):
    """
    Given a valid path to a pdf file, it returns the text of th pdf extracted with the library specified in the 'reader' input variable.

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
        except Exception as e:
            logging.error("An error occured while loading the document text with textract. The pdf version might be not supported.")
    return text


"""
The following functions are stand-alone routines which correspond to the different methods to find a doi
that are called by the pdf2doi routine (see pdf2doi.py)
"""

def find_doi_via_google_search(query, numb_results, func_validate_doi=validate):
    """
    Perform a google search with the keyword 'query', look at the first 'numb_results' and scan the text for any 
    possible DOI or arXiv identifier

    Parameters
    ----------
    query : string 
        string use for for google search
    numb_results : int
        how many results from the google query should be considered
    func_validate_doi : function, optional
        The function func_validate_doi must take one argument and return True/False.
        If func_validate_doi is specified, everytime that a possible DOI is identified the value 
        returned by func_validate_doi(DOI) is used to check if DOI is valid.
        
    Returns
    -------
    doi
        A valid DOI if any is found, or None if no DOI was found.
    """
    
    if not callable(func_validate_doi):
        func_validate_doi = lambda x : x
    doi = None
    desc = None
    i=1
    for url in search(query, stop=config.numb_results_google_search):
        logging.info(f"Trying locating the DOI in the search result #{str(i)}:{url}")
        i=i+1
        response = requests.get(url)
        text = response.text
        doi,desc = find_doi_in_text(text,func_validate_doi)
        
        if desc == 'doi':
            logging.info("A valid DOI was found in the document text.")
            
        if desc == 'arxiv':
            logging.info("A valid arXiv ID was found in the document text.")
        if doi:
            break
    return doi,desc

def find_doi_in_pdf_info(path,keysToCheckFirst=[],func_validate_doi=validate):
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
    func_validate_doi : function, optional
        The function func_validate_doi must take one argument and return True/False.
        If func_validate_doi is specified, everytime that a possible DOI is identified the value 
        returned by func_validate_doi(DOI) is used to check if DOI is valid.
        
    Returns
    -------
    doi
        A valid DOI if any is found, or None if no DOI was found.
    """

    if not callable(func_validate_doi):
        func_validate_doi = lambda x : x
    info = get_pdf_info(path)
    if not(info): return None,None

    doi = None
    desc = None
    Keys = keysToCheckFirst + list(info.keys()) #Quick way to create a list of keys where the elements of keysToCheckFirst appear first. 
                                        #Some elements of keysToCheckFirst might be duplicated in 'Keys', but this is not a problem
                                        #because the corresponding element in the info dictionary is eliminated after being checked
    for key in Keys:
        if key in info.keys():
            doi,desc = find_doi_in_text(info[key],func_validate_doi)
            if desc == 'doi':
                logging.info(f"A valid DOI was found in the document info labelled \'{key}\'.")
            if desc == 'arxiv':
                logging.info(f"A valid arXiv ID was found in the document info labelled \'{key}\'.")
            if doi:
                break
            del info[key]

    return doi,desc

def find_doi_in_filename(path, func_validate_doi=validate):
    """ 
    Parameters
    ----------
    path : a valid path to a pdf file
    func_validate_doi : function, optional
        The function func_validate_doi must take one argument and return True/False.
        If func_validate_doi is specified, everytime that a possible DOI is identified the value 
        returned by func_validate_doi(DOI) is used to check if DOI is valid.
    Returns
    -------
    doi
        A valid DOI if any is found, or None if no DOI was found.
    """
    text = os.path.basename(path)
    doi,desc = find_doi_in_text([text],func_validate_doi)
    if desc == 'doi':
        logging.info("A valid DOI was found in the file name.")
    if desc == 'arxiv':
        logging.info("A valid arXiv ID was found in the file name.")
    return doi,desc


def find_doi_in_pdf_text(path, reader = 'pypdf', func_validate_doi=validate):
    """ Try to find a valid DOI in the plain text of the pdf file. We read the pdf page by page, and for each
    page we look for something that matches a DOI or an arXiv identifier by using the function find_doi_in_text()

    Parameters
    ----------
    path : a valid path to a pdf file
    reader : string, optional
        It specifies which library is used to extract the text from the pdf.
        The supported values are either 'pypdf' (uses the PyPDF2 module) or 'textract' (uses the 'textract' module)
    func_validate_doi : function, optional
        The function func_validate_doi must take one argument and return True/False.
        If func_validate_doi is specified, everytime that a possible DOI is identified the value 
        returned by func_validate_doi(DOI) is used to check if DOI is valid.
    Returns
    -------
    doi
        A valid DOI if any is found, or None if no DOI was found.
    """

    if not callable(func_validate_doi):
        func_validate_doi = lambda x : x
    
    texts = get_pdf_text(path,reader)
    if not isinstance(texts,list):
        texts = [texts]
    doi,desc = find_doi_in_text(texts,func_validate_doi)
    if desc == 'doi':
        logging.info("A valid DOI was found in the document text.")
    if desc == 'arxiv':
        logging.info("A valid arXiv ID was found in the document text.")

    return doi,desc

