from PyPDF2 import PdfFileReader
import requests
import os
import re
import bibtexparser
import argparse
import logging
from googlesearch import search

#folder = os.path.abspath(os.path.dirname(__file__))
#folder = 'D:\Dropbox (Personal)\PythonScripts\PaperRenamer'
#folder= folder + "/test/"
#os.chdir(folder)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def doi2bib(doi):
    """
    Return a bibTeX string of metadata for a given DOI.
    """
    url = "http://dx.doi.org/" + doi
    headers = {"accept": "application/x-bibtex"}
    r = requests.get(url, headers = headers)
    return r.text

def validate_doi(doi,check_also_online=1):
    """
    Check that doi is a valid DOI by using a regular expression.
    If check_also_online=true, it also checks that the doi is actually associate to a paper via a query to http://dx.doi.org/
    """
    if re.match(r'(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n]|$)',doi,re.I):
        if check_also_online:
            result = doi2bib(doi)
            if (result.lower().find( "DOI Not Found".lower() ))==-1:
                return True, result
            else:
                return False
        else:
            return True
    return False

def extract_doi_from_text(text,version=0):

    if version == 0:
        string = 'doi[\s\.\:]{0,2}(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n\"<]|$)' #version 0 looks for something like "DOI : 10.xxxxS[end characters]" 
                                                                              # where xxxx=4 digits, S=combination of characters, digits, ., :, -, and / of any length
                                                                              # [end characters] is either space, newline, " or <. Or th end of the string
                                                                              #The initial part could be either "DOI : ", "DOI", "DOI:", "DOI.:", ""DOI:." and with possible 
                                                                              #spaces or lower cases
    if version == 1:
        string = '(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n\"<]|$)'                #in version 1 the requirement of having "DOI : " in the beginning is removed

    if version == 2:
        string = '(10\.\d{4}[\:\.\-\/a-z]+[\:\.\-\d]+)(?:[\s\na-z\"<]|$)'    #version 2 is used for cases in which, in plain texts, the DOI is not followed by a space, newline or special characters,
                                                                             #but is instead followed by other letters. We can still isolate the DOI
                                                                             #by assumeing that DOI always ends up with numbers
    regexDOI = re.search(string,text,re.I)
    if regexDOI and validate_doi(regexDOI.group(1)):
        return regexDOI.group(1)

    return None

def pdf2doi(file,verbose=False):
    
    #The next 2 lines are needed to make sure that logging works also in Ipython
    from importlib import reload  # Not needed in Python 2
    reload(logging)

    # Setup logging
    if verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.CRITICAL

    logging.basicConfig(format="%(message)s", level=loglevel)

    file = open(file, 'rb') 
    pdf = PdfFileReader(file,strict=False)
    info = pdf.getDocumentInfo()

    #First method: we look for a string that can be a DOI in the values of the dictionary info.
    #We look into these fields with progressively looser and looser matching patterns, corresponding to increasing values of the variable v.
    logging.info("Trying locating the DOI in the document infos...")
    for v in range(3):
        for key, value in info.items():
            doi = extract_doi_from_text(value,version=v)
            if doi and validate_doi(doi):
                logging.info("\tA valid DOI was found in the document info labelled \'"+key+"\'.")
                return doi
    logging.info("\tCould not find the DOI in the document info.")


    #Second method: we look in the plain text of the pdf and try to find something that matches a DOI. 
    #We look for progressively more looser matching patterns, corresponding to increasing values of the variable v.
    logging.info("Trying locating the DOI in the document text...")
    number_of_pages = pdf.getNumPages()
    keep_looping_over_v = 1
    for v in range(3):
        for i in range(number_of_pages):
            try:
                pageObj = pdf.getPage(i)
                text = pageObj.extractText()
                doi = extract_doi_from_text(text,version=v)
                if doi and validate_doi(doi): 
                    logging.info("\tA valid DOI was found in the document text.")
                    return doi
            except Exception as e:
                logging.info("\tAn error occured while loading the document text with PyPDF2. The pdf version might be not supported.")
                keep_looping_over_v = 0
                break
        if keep_looping_over_v == 0: break


    logging.info("\tCould not find the DOI in the document text.")

    #Third method: we try to identify the title of paper in the info dictionary, do a google search, open the first result and look for DOI in the plain text.
    NumbResults = 6
    logging.info("Trying locating a possible title in the document infos...")
    FoundAnyPossibleTitle = 0
    for key, value in info.items():
        if 'title' in key.lower():
            FoundAnyPossibleTitle = 1
            logging.info("\tA possible title \"" + value +  "\" was found in the document info labelled \'" + key + "\'.")
            logging.info("\t\tDoing a google search, looking at the first " + str(NumbResults) + " results...")
            i=1
            for url in search(value, stop=NumbResults):
                logging.info("\t\tTrying locating the DOI in the search result #" + str(i) + ": " + url)
                i=i+1
                response = requests.get(url)
                text = response.text
                for v in range(3):
                    doi = extract_doi_from_text(text,version=v)
                    if doi and validate_doi(doi): 
                        logging.info("\t\tA valid DOI was found in this search result.")
                        return doi
            logging.info("\t\tNone of the search results contained a valid url.")
    if FoundAnyPossibleTitle == 0:
        logging.info("\tNo title was found in the document infos.")

    return None

def main():
    parser = argparse.ArgumentParser( 
                                    description = "Retrieve the DOI of a paper from a PDF file.",
                                    epilog = "")
    parser.add_argument(
                        "filename",
                        help = "Relative path of the pdf file.",
                        metavar = "filename")
    parser.add_argument(
                        "-v",
                        "--verbose",
                        help="Increase output verbosity.",
                        action="store_true")
    args = parser.parse_args()

    doi = pdf2doi(args.filename,args.verbose)
    print(doi)
    return

if __name__ == '__main__':
    main()