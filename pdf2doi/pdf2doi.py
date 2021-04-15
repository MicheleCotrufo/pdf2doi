import argparse
import logging
from os import path
import pdf2doi.DOI_finders as DOI_finders
import pdf2doi.config as config

def pdf2doi(filename,
            verbose=False,
            websearch=True,
            webvalidation=True,
            numb_results_google_search=config.numb_results_google_search):
    
    config.check_online_to_validate = webvalidation
    config.websearch = websearch
    config.numb_results_google_search = numb_results_google_search
    #The next 2 lines are needed to make sure that logging works also in Ipython
    from importlib import reload  # Not needed in Python 2
    reload(logging)

    # Setup logging
    if verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.ERROR
    logging.basicConfig(format="%(message)s", level=loglevel)

    if not path.exists(filename):
        logging.error("The file indicated does not exist.")
        return None

    if not filename.endswith('.pdf'):
        logging.error("The file must have .pdf extension.")
        return None
    
    #First method: we look for a string that can be a DOI in the values of the dictionary info = pdf.getDocumentInfo()
    #We first look for the elements with keys 'doi' or '/doi' (if the they exist, and then any other field of the dictionary info
    logging.info("Trying locating the DOI in the document infos...")
    doi,desc = DOI_finders.find_doi_in_pdf_info(filename,keysToCheckFirst=['doi','/doi'])
    if doi:
        return doi
    logging.info("Could not find the DOI in the document info.")
    logging.basicConfig(format="%(message)s", level=loglevel)


    #info = pdf.getDocumentInfo()
    
    #Second method: we look in the plain text of the pdf and try to find something that matches a DOI (or at least an arXiv ID). 
    #We look for progressively more looser matching patterns, corresponding to increasing values of the variable v.
    logging.info("Trying locating the DOI (or an arXiv ID) in the document text by using PyPDF...")
    doi,desc = DOI_finders.find_doi_in_pdf_text(filename, reader= 'pypdf')
    if doi:
        return doi
    logging.info("Could not find the DOI (or an arXiv ID) in the document text by using PyPDF.")
    
    #We repeat the same test but now using text_extractor = 'textract', which uses the module 'textract' to
    #extract text from the pdf. In certain istances textract seems to work better than PyPDF in extracting 
    #text near the margin of a page
    logging.info("Trying locating the DOI (or an arXiv ID) in the document text by using textract...")
    doi,desc = DOI_finders.find_doi_in_pdf_text(filename, reader= 'textract')
    if doi:
        return doi
    logging.info("Could not find the DOI (or an arXiv ID) in the document text by using textract.")


    #Third method: we try to identify the title of the paper, do a google search with it, open the first results and look for DOI in the plain text.
    doi = None

    logging.info("Trying locating a possible title in the document infos...")
    titles = DOI_finders.find_possible_titles(filename)
    FoundAnyPossibleTitle = 0
    if titles:
        if config.websearch==True:
            logging.info("\tPossible titles of the paper were found, but the web-search method is currently disabled by the user. Enable it in order to perform a qoogle query.")
        else:
            for title in titles:
                logging.info(f"\tA possible title was found: \"{title}\"")
                logging.info(f"\t\tDoing a google search, looking at the first {str(NumbResults)} results...")
                doi,desc = DOI_finders.find_doi_via_google_search(title, config.numb_results_google_search )
                if doi:
                    return doi
                logging.info("\t\tNone of the search results contained a valid DOI.")         
    else:
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
    parser.add_argument(
                        "-nws",
                        "--nowebsearch",
                        help="Disable any DOI retrieval method which requires internet searches (e.g. queries to google).",
                        action="store_true")
    parser.add_argument(
                        "-nwv",
                        "--nowebvalidation",
                        help="Disable the DOI online validation via query to http://dx.doi.org/.",
                        action="store_true")
    args = parser.parse_args()

    doi = pdf2doi(filename=args.filename,
                  verbose=args.verbose,
                  websearch=not(args.nowebsearch),
                  webvalidation=not(args.nowebvalidation))
    if doi:
        print(doi)
    return

if __name__ == '__main__':
    main()