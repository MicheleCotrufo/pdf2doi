import argparse
import logging
from os import path, listdir
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
    from importlib import reload 
    reload(logging)

    # Setup logging
    if verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.ERROR
    logging.basicConfig(format="%(message)s", level=loglevel)
    
    # Check if filename is a directory or a file
    
    #If it is a directory, we look for all the .pdf files or sub-directories,
    # and we call again this function
    if  path.isdir(filename):
        logging.info(f"Looking for pdf files in the folder {filename}...")
        pdf_files = [f for f in listdir(filename) if f.endswith('.pdf')]
        numb_files = len(pdf_files)
        logging.info(f"Found {numb_files} pdf files:")
        if not(filename.endswith("/")):
            filename = filename + "/"
        dois_in_this_folder = []
        for f in pdf_files:
            file = filename + f
            doi,desc = pdf2doi(file,
                    verbose=verbose,
                    websearch=websearch,
                    webvalidation=webvalidation,
                    numb_results_google_search=numb_results_google_search)
            logging.info(doi)
            dois_in_this_folder.append([f,doi,desc])
        return dois_in_this_folder
    #If it is not a directory, we check that it is an existing file and that it ends with .pdf
    else:
        logging.info(f"................") 
        logging.info(f"File: {filename}")  
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
        return doi,desc
    logging.info("Could not find the DOI in the document info.")
    logging.basicConfig(format="%(message)s", level=loglevel)

    #We look for a DOI or arxiv ID within the filename
    logging.info("Trying locating the DOI (or an arXiv ID) in the file name...")
    doi,desc = DOI_finders.find_doi_in_filename(filename)
    if doi:
        return doi,desc
    logging.info("Could not find the DOI (or an arXiv ID) in the file name.")
    logging.basicConfig(format="%(message)s", level=loglevel)

    
    #We look in the plain text of the pdf and try to find something that matches a DOI (or at least an arXiv ID). 
    #We look for progressively more looser matching patterns, corresponding to increasing values of the variable v.
    logging.info("Trying locating the DOI (or an arXiv ID) in the document text by using PyPDF...")
    doi,desc = DOI_finders.find_doi_in_pdf_text(filename, reader= 'pypdf')
    if doi:
        return doi,desc
    logging.info("Could not find the DOI (or an arXiv ID) in the document text by using PyPDF.")
    
    #We repeat the same test but now using text_extractor = 'textract', which uses the module 'textract' to
    #extract text from the pdf. In certain istances textract seems to work better than PyPDF in extracting 
    #text near the margin of a page
    logging.info("Trying locating the DOI (or an arXiv ID) in the document text by using textract...")
    doi,desc = DOI_finders.find_doi_in_pdf_text(filename, reader= 'textract')
    if doi:
        return doi,desc
    logging.info("Could not find the DOI (or an arXiv ID) in the document text by using textract.")


    #We try to identify the title of the paper, do a google search with it, open the first results and look for DOI in the plain text.
    doi = None

    logging.info("Trying locating a possible title in the document infos...")
    titles = DOI_finders.find_possible_titles(filename)
    FoundAnyPossibleTitle = 0
    if titles:
        if config.websearch==False:
            logging.warning("\tPossible titles of the paper were found, but the web-search method is currently disabled by the user. Enable it in order to perform a qoogle query.")
        else:
            for title in titles:
                logging.info(f"\tA possible title was found: \"{title}\"")
                logging.info(f"\t\tDoing a google search, looking at the first {str(config.numb_results_google_search)} results...")
                doi,desc = DOI_finders.find_doi_via_google_search(title, config.numb_results_google_search )
                if doi:
                    return doi,desc
                logging.info("\t\tNone of the search results contained a valid DOI.")         
    else:
        logging.info("No title was found in the document infos.")

    logging.error("It was not possible to find a DOI for this file.")
    return None,None

def main():
    parser = argparse.ArgumentParser( 
                                    description = "Retrieve the DOI of a paper from a PDF file.",
                                    epilog = "")
    parser.add_argument(
                        "filename",
                        help = "Relative path of the pdf file or of a folder.",
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
                        help="Disable the DOI online validation via queries (e.g., to http://dx.doi.org/).",
                        action="store_true")
    parser.add_argument('-google_results', 
                        help=f"Set how many results should be considered when doing a google search for the DOI (default={str(config.numb_results_google_search)}).",
                        action="store", dest="google_results", type=int)
    args = parser.parse_args()

    doi = pdf2doi(filename=args.filename,
                  verbose=args.verbose,
                  websearch=not(args.nowebsearch),
                  webvalidation=not(args.nowebvalidation),
                  numb_results_google_search=args.google_results)
    # if doi:
    #     print(doi)
    # return

if __name__ == '__main__':
    main()