"""
This module contains different functions to identify the DOI (or arXiv identifier) of a paper starting from a PDF file.
The module is divided in two parts. The first part contains low-level functions. These are functions that perform several small tasks 
(e.g., find a DOI in a string of text, validating a DOI, etc.) and that are not supposed to be called directly by the user or by 
any part of the main script main.py. Instead, they are called by the high-level finder functions, defined in the second part of 
this module.
"""
from itertools import accumulate
from PyPDF2 import PdfFileReader, PdfFileWriter
import textract
import requests
import pdftitle
import re
import logging
from googlesearch import search
import pdf2doi.config as config
import os
import feedparser

from pdf2doi.patterns import (
    arxiv2007_pattern,
    doi_regexp,
    arxiv_regexp,
    standardise_doi
)

logger = logging.getLogger('pdf2doi')

######## Beginning first part, low-level functions ######## 

def validate_doi_web(doi,method=None):
    """ It queries dx.doi.org for a certain doi, to check that the doi exists.
    If dx.doi.org could not find any paper associated to this doi, the function returns None
    If it was not possible to connect to dx.doi.org, the function returns -1
    If dx.doi.org confirmed that DOI exists, the function returns the full text obtained from dx.doi.org
    Depending on the value of method (default =config.get('method_dxdoiorg')), the format of the text returned by dx.doi.org will be different
    """
    if method == None:
        method = config.get('method_dxdoiorg')
    try:
        url = "http://dx.doi.org/" + doi
        headers = {"accept": method}
        NumberAttempts = 10
        while NumberAttempts:
            r = requests.get(url, headers = headers)
            r.encoding = 'utf-8' #This forces to encode the obtained text with utf-8
            text = r.text
            # 503 or 504 errors are common
            if r.status_code >= 500 or (text.lower().find("503 Service Unavailable".lower() )>=0) or (not text):
                NumberAttempts = NumberAttempts -1
                logger.info("Could not reach dx.doi.org. Trying again. Attempts left: " + str(NumberAttempts))
                continue
            else:
                NumberAttempts = 0
            if (text.lower().find( "DOI Not Found".lower() ))==-1:
                return text
                #metadata = parse_bib_from_dxdoiorg(text, method)
                #return {'bibtex_entry':make_bibtex(metadata), 'bibtex_data':metadata}
            else:
                return None
    except Exception as e:
        logger.error(r"Some error occured within the function validate_doi_web")
        logger.error(e)
        return -1

def validate_arxivID_web(arxivID):
    """It queries export.arxiv.org for a certain arxiv ID, to check that it exists.
    If export.arxiv.org could not find any paper associated to this arxiv ID, the function returns None
    If it was not possible to connect to export.arxiv.org, the function returns -1
    If export.arxiv.org confirmed that DOI exists, the function returns the data obtained from export.arxiv.org
    """
    try:
        url = "http://export.arxiv.org/api/query?search_query=id:" + arxivID
        result = feedparser.parse(url)
        items = result.entries[0]
        found = len(items) > 0
        if not found: 
            return None
        else:
            return items
    except Exception as e:
        logger.error(r"Some error occured within the function arxiv2bib")
        logger.error(e)
        return -1    

def validate(identifier,what='doi'):
    """
    Check that an identifier is a valid identifier by using a regular expression.
    If config.get('webvalidation') == true, it also checks that the identifier is actually associate to a paper via 
    a query to the proper website (e.g. http://dx.doi.org/ for DOIs).

    Parameters
    ----------
    identifier : string
        The identifier (e.g. doi or arXiv ID) to validate.
    what : string, optional. Possible values = 'doi' (default), 'arxiv'
        Specifies the kind of identifier to be validated.
    Returns
    -------
    result :    If config.get('webvalidation') is set to true but connection was not possible, it returns None
                If config.get('webvalidation') is set to true and the identifier is validated, it returns the validation object (could be either a string or dictionary)
                If config.get('webvalidation') is set to false, it returns a single boolean value (True if identifier is valid, False if is not valid)
    """  
    if not identifier:
        return None
    if what=='doi':
        doi_id = standardise_doi(identifier)
        if identifier != doi_id:
            logger.info(f"Standardised DOI: {identifier} -> {doi_id}")

        if doi_id:
            if config.get('webvalidation'):
                logger.info(f"Validating the possible DOI {doi_id} via a query to dx.doi.org...")
                result = validate_doi_web(doi_id)
                if result==-1:
                    logger.error(f"Some error occured during connection to dx.doi.org.")
                    return None
                if isinstance(result,str) and result.strip()[0:5] == '@misc':
                    logger.error(f"The DOI was validated by by dx.doi.org, but the validation string starts with the tag \"@misc\". This might be the DOI of the journal and not the article itself.")
                    return False
                if result:
                    logger.info(f"The DOI {doi_id} is validated by dx.doi.org.")
                    return result
                else:
                    logger.info(f"The DOI {doi_id} is not valid according to dx.doi.org.")
                    return False
            else:
                logger.info(f"NOTE: Web validation is deactivated. Set webvalidation = True (or remove the '-nwv' argument if working from command line) in order to validate a potential DOI on dx.doi.org.")
                return True
        else: return False

    elif what=='arxiv':
        if re.match(arxiv2007_pattern,identifier,re.I):
            if config.get('webvalidation'):
                logger.info(f"Validating the possible arxiv ID {identifier} via a query to export.arxiv.org...")
                result = validate_arxivID_web(identifier)
                if result==-1:
                    logger.error(f"Some error occured during connection to export.arxiv.org.")
                    return None
                if result:
                    logger.info(f"The Arxiv ID {identifier} is validated by export.arxiv.org")
                    return result
                else:
                    logger.info(f"The Arxiv ID {identifier} is not valid according to export.arxiv.org.")
                    return False
            else:
                logger.info(f"NOTE: Web validation is deactivated. Set webvalidation = True (or remove the '-nwv' argument if working from command line) in order to validate a potential arxiv ID on export.arxiv.org.")
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
    arxivID : list
        It returns a list of all arXiv IDs found (or empty list if no ID was found)
    """   
    try:                                            
        arxiv_ids = re.findall(arxiv_regexp[version] ,text,re.I)
        return arxiv_ids
    except:
        pass
    return []

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
    doi_list : list
        It returns a list of all dois found (or empty list if no doi was found)

    """    
    try:
        # TODO: Consider lookahead wrapping
        # # Wrap in lookahead to allow overlapping matches
        # dois = re.findall(f"(?={doi_regexp[version]})",text,re.I)
        dois = re.findall(doi_regexp[version],text,re.I)
        return dois
    except:
        pass
    return []

def find_identifier_in_google_search(query,func_validate,numb_results):
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}

    MaxLengthDisplay = 100
    if len(query)>MaxLengthDisplay:
        query_to_display = query[0:MaxLengthDisplay]  + " ...[query too long, the remaining part is suppressed in the logging]"
    else:
        query_to_display = query
    logger.info(f"Performing google search with key \"" + query_to_display + "\"")
    logger.info(f"and looking at the first {numb_results} results...")
    i=1
    try:
        for url in search(query, stop=numb_results):
            identifier,desc,info = find_identifier_in_text([url],func_validate)
            if identifier: 
                logger.info(f"A valid {desc} was found in the search URL.")
                return identifier,desc,info
            logger.info(f"Looking for a valid identifier in the search result #{str(i)} : {url}")
            response = requests.get(url,headers=headers)
            text = response.text
            identifier,desc,info = find_identifier_in_text(text,func_validate)
            if identifier: 
                return identifier,desc,info
            i=i+1
    except Exception as e: 
        logger.error('Some error occured while doing a google search (maybe the string is too long?): \n '+ str(e))
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
    func_validate : function
        The function func_validate is used to validate any identifier that is found. 
        It must take two input arguments, first one being the identifier to validate and the second one being the type
        of identifier (e.g. 'doi,''arxiv') and return False when the identifier is not valid and either True or a non-empty string
        when the identifier is valid. For most application func_validate can be set equal to the function validate defined in this same module.  
        
    Returns
    -------
    identifier : string
        A valid identifier if any is found, or None if nothing was found.
    desc : string
        Description of what was found (e.g. 'doi,''arxiv')
    validation : string or True
        The output returned by the function func_validate. If web validation is enabled, this is typically a bibtex entry for this 
        publication. Otherwise, it is just equal to True

    """
    if not isinstance(texts,list): texts = [texts]
    
    for text in texts:

        if isinstance(text, bytes):
            text = text.decode()
        #First we look for DOI
        for v in range(len(doi_regexp)):
            identifiers = extract_doi_from_text(text,version=v)
            for identifier in identifiers:
                logger.debug("Found a potential DOI: " + identifier)
                validation = func_validate(identifier,'doi')
                if validation: 
                    return identifier, 'DOI', validation
            
        #Then we look for an Arxiv ID
        for v in range(len(arxiv_regexp)):
            identifiers = extract_arxivID_from_text(text,version=v)
            for identifier in identifiers:
                validation = func_validate(identifier,'arxiv')
                if validation:
                    return identifier,'arxiv ID', validation
    return None, None, None


def get_pdf_info(file):
    """
    Given a valid file object, it returns a dictionary of info. 
    Currently, it uses PyPDF to extract the info.
    
    Parameters
    ----------
    file : file object, opened as 'rb
    
    Returns
    -------
    info : dictionary
    """

    try:
        pdf = PdfFileReader(file,strict=False)
    except Exception as e:
        logger.error("It was not possible to open the file with PyPDF2. Is this a valid pdf file?")
        logger.error(f"{e}")
        return None
    try:
        info = pdf.getDocumentInfo()
    except Exception as e:
        logger.error(f"An error occurred when retrieving the pdf info with PyPDF2: {e}")
        return None

    #file.close()
    return info
    
def find_possible_titles(file):
    """
    Given a valid file object, it tries to extract a list of possible titles. 
    In the current implementation it looks for titles by 1) looking for the outcome of pdftitle library, 
    2) looking in the dictionary returned by the PyPDF library and 3) looking in the filename.

    Parameters
    ----------
    file : file object, opened as 'rb
    
    Returns
    -------
    titles : list of strings
        Possible titles of the paper.
    """
    titles = []
    # (1)    
    try:
        title = pdftitle.get_title_from_io(file)
    except:
        title = ''
    if not(isinstance(title, str)):
        return
    if len(title.strip())>12:#This is to check that the title found is neither empty nor just few characters
        titles.append(title)  
        
    # (2)
    info = get_pdf_info(file)
    if not(info): return None
    
    for key, value in info.items():
        if 'title' in key.lower():
            if isinstance(value,str) and len(value.strip())>12 and len(value.split())>3: #This is to check that the title found is neither empty nor just few characters or few words
                titles.append(value)         
    # (3)
    title = os.path.basename(file.name)
    if len(title.strip())>30:#This is to check that the title found is neither empty nor just few characters
        titles.append(title)
        
    return titles
        
def get_pdf_text(file,reader):
    """
    Given a valid file object (pointing to a pdf file), it returns the text of the pdf file extracted with the library 
    specified in the 'reader' input variable.

    Parameters
    ----------
    file : file object, opened as 'rb
    reader : string
        It specifies which library is used to extract the text from the pdf.
        The supported values are either 'pypdf' (uses the PyPDF2 module) or 'textract' (uses the 'textract' module)
    Returns
    -------
    text : list of strings
    """
    text =[]
    if reader == 'pypdf':
        try:
            pdf = PdfFileReader(file,strict=False)
        except Exception as e:
            logger.error(f"An error occurred when reading the content of this file with PyPDF2.")
            logger.error("Error from PyPDF2: " + str(e))
            return None
        try:
            number_of_pages = pdf.getNumPages()
        except Exception as e:
            logger.error(f"An error occurred when retrieving the number of pages in the pdf with PyPDF2.")
            logger.error("Error from PyPDF2: " + str(e))
            return None
            
        for i in range(number_of_pages):
            try:
                text.append( (pdf.getPage(i)).extract_text())
            except Exception as e:
                logger.error("An error occured while loading the document text with PyPDF2. The pdf version might be not supported.")
                logger.error("Error from PyPDF2: " + str(e))
                break 
    if reader == 'textract':
        #This block of code is not very efficient. We start from an object file (file), we extract its path, and then we pass this path to the library
        #textract, which will later re-open the file; however, right now there isn't a workaround, because textract does not accept an object file as input.
        path = file.name #Note: this part will fail with if the object file does not correpond to a locally available file
        try:
            text = [textract.process(path,encoding='utf-8', errors='ignore').decode('utf-8')]
        except Exception as e:
            logger.error(e)
            try:
                text = [textract.process(path)]
            except Exception as e:   
                logger.error("An error occured while loading the document text with textract. The pdf version might be not supported.")
                logger.error("Error from textract: " + str(e))
    return text

def add_found_identifier_to_metadata(target,identifier):
    """Given a pdf file or a folder identified by the input variable target, it adds a metadata with label '/identifier'
    and containing the content of the input variable identifier to all pdf files specified by target (either a single file or
    all the pdf files in a folder). This can be useful to make sure that the next time
    this same pdf is analysed, the identifier is found more easily.
    It can also be useful when one want to reset to '' the '/identifier' of all pdf files in a certain folder.

    Parameters
    ----------
    target : string
        a valid path to a pdf file or a folder
    identifier : string
        a valid identifier, which will be stored in the pdf metadata with name '/identifier'
    Returns
    -------
    True if the the metadata was added succesfully, false otherwise
    """
    list_files = []
    if  os.path.isdir(target): #if target is a folder, we populate the list list_files with all the pdf files contained in this folder
        logger.info(f"Looking for pdf files in the folder {target}...")
        pdf_files = [f for f in os.listdir(target) if (f.lower()).endswith('.pdf')]
        numb_files = len(pdf_files)
        if len(pdf_files) == 0:
            logger.error("No pdf files found in this folder.")
            return None
        logger.info(f"Found {numb_files} pdf files.")
        if not(target.endswith(config.get('separator'))): #Make sure the path ends with "\" or "/" (according to the OS)
            target = target + config.get('separator')
        for f in pdf_files:
            list_files.append(target + f)
    else:
        list_files = [target]

    for f in list_files:
        logger.info(f"Trying to write the identifier \'{identifier}\' into the metadata of the file \'{f}\'...")
        try:
            file = open(f, 'rb') 
        except (FileNotFoundError, IOError):
            msg = "File not found."
            logger.error(msg)
            return False, msg
        try:
            pdf = PdfFileReader(f,strict=False)
        except:
            msg = "It was not possible to open the file with PyPDF2. Is this a valid pdf file?"
            logger.error(msg)
            return False, msg
        try:
            writer = PdfFileWriter()
            writer.appendPagesFromReader(pdf)
            metadata = pdf.getDocumentInfo()
            try:
                writer.add_metadata(metadata)    #This instruction might generate an error if the pre-existing metadata are weird and are not
            except:                             #correctly seen as strings (it happens with old files). Therefore we use the try/except
                pass                            #to ignore this possible problem
            key = '/identifier'
            writer.add_metadata({
                key: identifier
            })
            fout = open(f, 'ab') 
            writer.write(fout)
            file.close()
            fout.close()
            logger.info(f"The identifier \'{identifier}\' was added succesfully to the metadata of the file \'{f}\' with key \'{key}\'...")
        except Exception as e:
            logger.error("Error from PyPDF2: " + str(e))
            msg = f"An error occured while trying to write the identifier \'{identifier}\' into the metadata of the file \'{f}\'. Maybe the file is open elsewhere?"
            logger.error(msg)
            return False, msg


######## End first part ######## 

###########################################################################################################
###########################################################################################################
###########################################################################################################

######## Beginning second part, high-level functions ######## 

'''
The following functions are high-level identifier finders, i.e. functions that can be called directly by the user or by the function pdf2doi
contained in main.py. The function find_identifier acts as a wrapper for all the other high-level functions: 
based on the value of the input argument method, it call the corresponding function. 
The correspondence between the values of the string method and the function to call is defined in the dictionary finder_methods 
(see bottom of this module).
'''



def find_identifier(file, method, func_validate=validate,**kwargs):
    """ Tries to find an identifier (e.g. DOI, arxiv ID,...) for the pdf file identified by the input
    argument 'file', by using the method specified by input argument 'method'. Any found identifier is validated
    by using the function func_validate. If a valid identifier is found with any method different from
    "document_infos" (i.e. by looking into the file metadata) the identifier is also added to the file metadata
    with key "/identifier" (unless config.get('save_identifier_metadata') is set to False)

    Parameters
    ----------
    file : object file 
    method : string
        Method to be used to look for an identifier. The possible values are specified by the keys of 
        the dictionary finder_methods.
    func_validate : function, optional, the default value is the validate() function defined in this module
        The function func_validate is used to validate any identifier that is found. 
        It must take two input arguments, first one being the identifier to validate and the second one being the type
        of identifier (e.g. 'doi,''arxiv') and return False when the identifier is not valid and either True or a non-empty string
        when the identifier is valid. 
    kwargs : 
        additional input parameters specific to the method chosen
        
    Returns
    -------
    result : dictionary
        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper. If config.get('webvalidation') = True, then result['validation_info']
                                    will typically contain a raw bibtex data for this paper. Otherwise it will just contain True                         
        result['path'] = path of the pdf file
        result['method'] = method used to find the identifier

    """
    if not method in  finder_methods.keys():
        raise ValueError("The input variable method is not valid. Possible values = \'" + "\',\'".join(finder_methods.keys())+"\'")
    if not callable(func_validate):  func_validate = lambda x : x

    identifier, desc, info = finder_methods[method](file,func_validate,**kwargs)
    
    result = {'identifier':identifier,'identifier_type':desc,
              'path':file.name, 'method':method}
    result['validation_info'] = info

    return result

def find_identifier_in_pdf_info(file,func_validate,keysToCheckFirst=[]):
    """ 
    Try to find a valid DOI in the values of the 'document information' dictionary. If a list of string is specified via the optional
    input parameter 'keysToCheckFirst', then the corresponding elements of the dictionary (assuming that the key exists) are given
    priority.

    Parameters
    ----------
    file : object file 
    keysToCheckFirst : list, optional
        A list of strings. If specified, element of the 'document information' dictionary with these keys (assuming that 
       they exist) are given priority in the DOI search (following the order they appear in this list)
    Returns
    -------
    result : dictionary with identifier and other info (see above) 
    """


    #This is a list of keys that will NOT be considered when looking for an identifier in the metadata. 
    #Some of them are known to contain doi-like patterns but not the actual doi of the publication.
    #For example '/wps-journaldoi' contains the DOI of the journal
    KeysNotToUse = ['/wps-journaldoi'] 
    pdfinfo = get_pdf_info(file)
    identifier, desc, info = None, None, None
    if pdfinfo:
        Keys = keysToCheckFirst + list(pdfinfo.keys()) #Quick way to create a list of keys where the elements of keysToCheckFirst appear first. 
                                            #Some elements of keysToCheckFirst might be duplicated in 'Keys', but this is not a problem
                                            #because the corresponding element in the pdfinfo dictionary is eliminated after being checked
        for key in Keys:
            if key in pdfinfo.keys() and key.lower() not in KeysNotToUse:
                identifier,desc,info = find_identifier_in_text(pdfinfo[key],func_validate)
                if identifier: 
                    logger.info(f"A valid {desc} was found in the document info labelled \'{key}\'.")
                    break
                del pdfinfo[key]
    if identifier:
        return identifier,desc,info
    else:
        logger.info("Could not find a valid identifier in the document info.")
        return None, None, None

def find_identifier_in_filename(file, func_validate):
    """ 
    Parameters
    ----------
    file : object file 
    func_validate : function
    Returns
    -------
    result : dictionary with identifier and other info (see above)
    """
    text = os.path.basename(file.name)
    strip_possible_extensions = list(accumulate(text.split('.'), lambda x,y: '.'.join([x, y])))
    texts = [text] + list(reversed(strip_possible_extensions))

    identifier,desc,info = find_identifier_in_text(texts,func_validate)
    if identifier: 
        logger.info(f"A valid {desc} was found in the file name.")
        return identifier,desc,info
    else:
        logger.info("Could not find a valid identifier in the file name.")
        return None, None, None

def find_identifier_in_pdf_text(file, func_validate):
    """ Try to find a valid identifier in the plain text of the pdf file. The text is extracted via the function
    get_pdf_text.

    Parameters
    ----------
    file : object file 
    func_validate : function
    Returns
    -------
    result : dictionary with identifier and other info (see above)
    """
    for reader in reader_libraries:
        logger.info(f"Extracting text with the library {reader}...")
        texts = get_pdf_text(file,reader.lower())
        
        if not isinstance(texts,list):
            texts = [texts]
        if texts:
            logger.info(f"Text extracted succesfully. Looking for an identifier in the text...")
            identifier,desc,info = find_identifier_in_text(texts,func_validate)
            if identifier: 
                logger.info(f"A valid {desc} was found in the document text.")
                return identifier,desc,info
            else:
                logger.info(f"Could not find a valid identifier in the document text extracted by {reader}.")
    logger.info("Could not find a valid identifier in the document text.")
    return None, None, None

def find_identifier_by_googling_title(file, func_validate):
    """
    Parameters
    ----------
    file : object file 
    func_validate : function, optional
    """
    titles = find_possible_titles(file)
    if titles:
        if config.get('websearch')==False:
            logger.info("NOTE: Possible titles of the paper were found, but the web-search method is currently disabled by the user. Enable it in order to perform a qoogle query.")
            return None, None, None
        else:
            logger.info(f"Found {len(titles)} possible title(s).")
            titles.sort(key=len, reverse=True)
            for index_title,title in enumerate(titles):
                logger.info(f"Trying possible title #{index_title+1}")
                identifier,desc,info = find_identifier_in_google_search(title,func_validate,numb_results=config.get('numb_results_google_search'))
                if identifier:
                    logger.info(f"A valid {desc} was found with this google search.")
                    return identifier,desc,info
            logger.info("None of the search results contained a valid identifier.")     
            return None, None, None
    else:
        logger.error("It was not possible to find a title for this file.")
        return None, None, None
    
def find_identifier_by_googling_first_N_characters_in_pdf(file, func_validate, numb_results=config.get('numb_results_google_search'), numb_characters=config.get('N_characters_in_pdf')):
    """
    Parameters
    ----------
    file : object file 
    func_validate : function, optional
    numb_results : int
    numb_characters : int
    """
    if config.get('websearch')==False:
        logger.info("NOTE: Web-search methods are currently disabled by the user. Enable it in order to use this method.")
        return None, None, None

    for reader in reader_libraries:
        logger.info(f"Trying to extract the first {numb_characters} characters from the pdf file by using the library {reader}...")
        text = get_pdf_text(file,reader.lower())
        if text==[] or text=="":
            logger.error(f"The library {reader} could not extract any text from this file.")
            continue
        if isinstance(text,list):
            text = "".join(text)
        if not(isinstance(text, str)):
            logger.error(f"The library {reader} could not extract any text from this file.")
            continue 
        text = re.sub(r'[^\x00-\x7f]',r' ',text)    #Remove all non-text characters from the string text
        for r in ("\n","\r","\t"):
            text = text.replace(r," ")
         
        if text=="":                                #Check tha the string is still not empty after removing non-text characters
            logger.error(f"The library {reader} could not extract any meaningful text from this file.")
            continue
            
        text = text[0:numb_characters]              #Select the first numb_characters characters

        logger.info(f"Doing a google search, looking at the first {config.get('numb_results_google_search')} results...")
        identifier,desc,info = find_identifier_in_google_search(text,func_validate,numb_results)
        if identifier:
            logger.info(f"A valid {desc} was found with this google search.")
            return identifier,desc,info

    logger.info(f"Could not find a valid identifier by googling the first {numb_characters} characters extracted from the pdf file.")
    return None, None, None
        
#The dictionary finder_methods list all the methods currently implemented to find an identifier.
#Each method is associated to a function.
#The keys of this dictionary corresponds to the possible values of the input argument 'method' 
#passed the function find_identifier
finder_methods = {
                    "document_infos"            : find_identifier_in_pdf_info,
                    "document_text"             : find_identifier_in_pdf_text,
                    "filename"                  : find_identifier_in_filename,
                    "title_google"              : find_identifier_by_googling_title,
                    "first_N_characters_google" : find_identifier_by_googling_first_N_characters_in_pdf
                    }

reader_libraries = ['PyPdf','textract']

######## End second part ######## 
