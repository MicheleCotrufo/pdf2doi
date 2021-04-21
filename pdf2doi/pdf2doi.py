import argparse
import logging
from os import path, listdir
import pdf2doi.finders as finders
import pdf2doi.config as config


def make_file_identifiers(filename_identifiers, identifiers):
    ''' Write all identifiers in the input list 'identifiers' into a text file with a path specified by filename_identifiers
    
    Parameters
    ----------
    filename_identifiers : string
        Absolute path of the target file.
    identifiers : list of dictionaries
        Each element of identifiers describes a .pdf file and contain the its identifier in the 'identifier' key and other infos.

    Returns
    -------
    None.
    '''
    with open(filename_identifiers, "w", encoding="utf-8") as text_file:
        for result in identifiers:
            text_file.write('{:<15s} {:<40s} {:<10s}\n'.format(result['identifier_type'], result['identifier'],result['path']) ) 
          
def make_file_bibtex(filename_bibtex, identifiers):
    '''Write all available bibtex entries from the input list 'identifiers' into a text file with a path specified by filename_bibtex
    
    Parameters
    ----------
    filename_bibtex : string
        Absolute path of the target file.
    identifiers : list of dictionaries
        Each element of identifiers describes a .pdf file and contain the its identifier in the 'identifier' key and other infos.

    Returns
    -------
    None.

    '''
    with open(filename_bibtex, "w", encoding="utf-8") as text_file:
        for result in identifiers:
            if isinstance(result['validation_info'],str):
                text_file.write(result['validation_info'] + "\n\n") 


def pdf2doi(target, verbose=False, websearch=True, webvalidation=True,
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
    
    config.check_online_to_validate = webvalidation
    config.websearch = websearch
    config.numb_results_google_search = numb_results_google_search
    
    #The next 2 lines are needed to make sure that logging works also in Ipython
    from importlib import reload 
    reload(logging)

    # Setup logging
    if verbose: loglevel = logging.INFO
    else: loglevel = logging.ERROR
    logging.basicConfig(format="%(message)s", level=loglevel)
      
    #Check if target is a directory
    #If yes, we look for all the .pdf files inside it, and for each of them
    #we call again this function
    if  path.isdir(target):
        logging.info(f"Looking for pdf files in the folder {target}...")
        pdf_files = [f for f in listdir(target) if f.endswith('.pdf')]
        numb_files = len(pdf_files)
        
        if numb_files == 0:
            logging.error("No pdf files found in this folder.")
            return None
        
        logging.info(f"Found {numb_files} pdf files.")
        if not(target.endswith(config.separator)): #Make sure the path ends with "\" or "/" (according to the OS)
            target = target + config.separator
            
        identifiers_found = [] #For each pdf file in the target folder we will store a dictionary inside this list
        for f in pdf_files:
            file = target + f
            result = pdf2doi(file, verbose=verbose, websearch=websearch, webvalidation=webvalidation,
                    numb_results_google_search=numb_results_google_search)
            logging.info(result['identifier'])
            identifiers_found.append(result)

        logging.info("................") 

        #If a string was passed via the argument filename_identifiers, 
        #we save all found identifiers in a text file with name = filename_identifiers
        if isinstance(filename_identifiers,str):
            try:
                make_file_identifiers(target+filename_identifiers, identifiers_found)
                logging.info(f'All found identifiers were saved in the file {filename_identifiers}')
            except Exception as e:
                logging.error(e)
                logging.error(f'A problem occurred when trying to write into the file {filename_identifiers}')
                
        #If a string was passed via the argument filename_bibtex, and if the online validation was used
        #we save all the bibtex entries collected during validation in a file with name = filename_bibtex
        if isinstance(filename_bibtex,str) and config.check_online_to_validate:
            try:
                make_file_bibtex(target+filename_bibtex, identifiers_found)
                logging.info(f'All available bibtex entries were stored in the file {filename_bibtex}')
            except Exception as e:
                logging.error(e)
                logging.error(f'A problem occurred when trying to write into the file {filename_bibtex}')
            
        return identifiers_found
    
    #If target is not a directory, we check that it is an existing file and that it ends with .pdf
    else:
        filename = target
        logging.info(f"................") 
        logging.info(f"File: {filename}")  
        if not path.exists(filename):
            logging.error("The file indicated does not exist.")
            return None    
        if not filename.endswith('.pdf'):
            logging.error("The file must have .pdf extension.")
            return None
        
        #Several methods are now applied to find a valid identifier in the .pdf file identified by filename
    
        #First method: we look into the pdf metadata (in the current implementation this is done
        # via the getDocumentInfo() method of the library PyPdf) and see if any of them is a string which containts a
        #valid identifier inside it. We first look for the elements of the dictionary with keys 'doi' or '/doi' (if the they exist), 
        #and then any other field of the dictionary
        result = finders.find_identifier(filename,method="document_infos",keysToCheckFirst=['doi','/doi'])
        if result['identifier']:
            return result 
        
        #Second method: We look for a DOI or arxiv ID inside the filename
        result = finders.find_identifier(filename,method="filename")
        if result['identifier']:
            return result 
    
        #Third method: We look in the plain text of the pdf and try to find something that matches a valid identifier. 
        result =  finders.find_identifier(filename,method="document_text")
        if result['identifier']:
            return result 
    
        
        #Fourth method: We look for possible titles of the paper, do a google search with them, 
        # open the first results and look for identifiers in the plain text of the obtained by the results.
        result =  finders.find_identifier(filename,method="title_google")
        if result['identifier']:
            return result
    
        logging.error("It was not possible to find a valid identifier for this file.")
        return result #This will be a dictionary with all entries as None

def main():
    parser = argparse.ArgumentParser( 
                                    description = "Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a publications.",
                                    epilog = "")
    parser.add_argument(
                        "path",
                        help = "Relative path of the pdf file or of a folder.",
                        metavar = "path")
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
    parser.add_argument(
                        "-s",
                        "--save_identifiers",
                        nargs='?',
                        const = False,
                        dest="filename_identifiers",
                        help="Save all the DOIs/identifiers found in the target folder in a .txt file inside the same folder (only available when a folder is targeted).",
                        action="store")
    parser.add_argument(
                        "-b",
                        "--make_bibtex",
                        nargs='?',
                        const = False,
                        dest="filename_bibtex",
                        help="Create a file with bibtex entries for each .pdf file in the targer folder (for which a valid identifier was found). This option is only available when a folder is targeted, and when the web validation is allowed.",
                        action="store")
    
    args = parser.parse_args()
    results = pdf2doi(target=args.path,
                  verbose=args.verbose,
                  websearch=not(args.nowebsearch),
                  webvalidation=not(args.nowebvalidation),
                  numb_results_google_search=args.google_results,
                  filename_identifiers = args.filename_identifiers,
                  filename_bibtex = args.filename_bibtex
                  )
        
    for result in results:
        if result['identifier']:
            print('{:<15s} {:<40s} {:<10s}\n'.format(result['identifier_type'], result['identifier'],result['path']) ) 

    return

if __name__ == '__main__':
    main()