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
        Each element of the list 'identifiers' describes a .pdf file and contains the its identifier in the 'identifier' key and other infos.
    Returns
    -------
    None.

    '''
    with open(filename_bibtex, "w", encoding="utf-8") as text_file:
        for result in identifiers:
            if isinstance(result['validation_info'],str):
                text_file.write(result['validation_info'] + "\n\n") 


def pdf2doi(target, verbose=False, websearch=True, webvalidation=True,
            save_identifier_metadata = config.save_identifier_metadata,
            numb_results_google_search=config.numb_results_google_search,
            filename_identifiers = False, filename_bibtex = False):
    ''' This is the main routine of the library. When the library is used as a command-line tool (via the entry-point "pdf2doi") the input arguments
    are collected, validated and sent to this function (see the function main () below).
    The function tries to extract the DOI (or other identifiers) for the pdf file in the path specified by the user in the input variable target. 
    If target contains the valid path of a folder, the function tries to extract the DOI/identifer of all pdf files in the folder.
    It returns a dictionary (or a list of dictionaries) containing info(s) about the file(s) examined, or None if an error occurred.
    By specifying valid values for the input variables filename_identifiers and filename_bibtex, all identifiers found and/or bibtex entries for
    all pdf files can be saved in text files (see description of input arguments for details)

    Example:
        import pdf2doi
        path = r"Path\to\folder"
        result = pdf2doi.pdf2doi(path, verbose=True)
        print(result[0]['identifier'])          # Print doi/identifier of the first pdf file found in this folder
        print(result[0]['identifier_type'])     # Print the type of identifier found (e.g. 'doi' or 'arxiv')
        print(result[0]['method'])              # Print the method used to find the identifier

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
    config.save_identifier_metadata = save_identifier_metadata
    if numb_results_google_search:
        config.numb_results_google_search = numb_results_google_search

    # Setup logging
    if verbose: loglevel = logging.INFO
    else: loglevel = logging.CRITICAL

    logger = logging.getLogger("pdf2doi")
    logger.setLevel(level=loglevel)
      
    #Check if target is a directory
    #If yes, we look for all the .pdf files inside it, and for each of them
    #we call again this function
    if  path.isdir(target):
        logger.info(f"Looking for pdf files in the folder {target}...")
        pdf_files = [f for f in listdir(target) if f.endswith('.pdf')]
        numb_files = len(pdf_files)
        
        if numb_files == 0:
            logger.error("No pdf files found in this folder.")
            return None
        
        logger.info(f"Found {numb_files} pdf files.")
        if not(target.endswith(config.separator)): #Make sure the path ends with "\" or "/" (according to the OS)
            target = target + config.separator
            
        identifiers_found = [] #For each pdf file in the target folder we will store a dictionary inside this list
        for f in pdf_files:
            logger.info("................") 
            file = target + f
            #For each file we call again this function, but now the input argument target is set to the path of the file
            result = pdf2doi(   target=file, verbose=verbose, websearch=websearch, webvalidation=webvalidation,
                                save_identifier_metadata = config.save_identifier_metadata,
                                numb_results_google_search=numb_results_google_search)
            logger.info(result['identifier'])
            identifiers_found.append(result)

        logger.info("................") 

        #If a string was passed via the argument filename_identifiers, 
        #we save all found identifiers in a text file with name = filename_identifiers
        if isinstance(filename_identifiers,str):
            try:
                make_file_identifiers(target+filename_identifiers, identifiers_found)
                logger.info(f'All found identifiers were saved in the file {filename_identifiers}')
            except Exception as e:
                logger.error(e)
                logger.error(f'A problem occurred when trying to write into the file {filename_identifiers}')
                
        #If a string was passed via the argument filename_bibtex, and if the online validation was used
        #we save all the bibtex entries collected during validation in a file with name = filename_bibtex
        if isinstance(filename_bibtex,str) and config.check_online_to_validate:
            try:
                make_file_bibtex(target+filename_bibtex, identifiers_found)
                logger.info(f'All available bibtex entries were stored in the file {filename_bibtex}')
            except Exception as e:
                logger.error(e)
                logger.error(f'A problem occurred when trying to write into the file {filename_bibtex}')
            
        return identifiers_found
    
    #If target is not a directory, we check that it is an existing file and that it ends with .pdf
    else:
        filename = target
        logger.info(f"File: {filename}")  
        if not path.exists(filename):
            logger.error(f"'{filename}' is not a valid file or directory.")
            return None    
        if not filename.endswith('.pdf'):
            logger.error("The file must have .pdf extension.")
            return None
        
        #Several methods are now applied to find a valid identifier in the .pdf file identified by filename
    
        #First method: we look into the pdf metadata (in the current implementation this is done
        # via the getDocumentInfo() method of the library PyPdf) and see if any of them is a string which containts a
        #valid identifier inside it. We first look for the elements of the dictionary with keys 'doi' or '/doi' (if the they exist), 
        #and then any other field of the dictionary
        result = finders.find_identifier(filename,method="document_infos",keysToCheckFirst=['/doi','/identfier'])
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
        # open the first results and look for identifiers in the plain text of the searcg results.
        result =  finders.find_identifier(filename,method="title_google")
        if result['identifier']:
            return result
        
        #Fifth method: We extract the first N characters from the file (where N is set by config.N_characters_in_pdf) and we use it as 
        # a query for a google seaerch. We open the first results and look for identifiers in the plain text of the searcg results.
        result =  finders.find_identifier(filename,method="first_N_characters_google")
        if result['identifier']:
            return result

        logger.error("It was not possible to find a valid identifier for this file.")
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
                        "-nv",
                        "--no_verbose",
                        help="Decrease verbosity.",
                        action="store_true")
    parser.add_argument(
                        "-nws",
                        "--no_web_search",
                        help="Disable any method to find identifiers which requires internet searches (e.g. queries to google).",
                        action="store_true")
    parser.add_argument(
                        "-nwv",
                        "--no_web_validation",
                        help="Disable the online validation of identifiers (e.g., via queries to http://dx.doi.org/).",
                        action="store_true")
    parser.add_argument(
                        "-nsim",
                        "--no_store_identifier_metadata",
                        help="By default, anytime an identifier is found it is added to the metadata of the pdf file (if not present yet). By setting this parameter, the identifier is not stored in the file metadata.",
                        action="store_true")
    parser.add_argument('-google_results', 
                        help=f"Set how many results should be considered when doing a google search for the DOI (default={str(config.numb_results_google_search)}).",
                        action="store", dest="google_results", type=int)
    parser.add_argument(
                        "-s",
                        "--save_identifiers_file",
                        dest="filename_identifiers",
                        help="Save all the identifiers found in the target folder in a text file inside the same folder with name specified by FILENAME_IDENTIFIERS (only available when a folder is targeted).",
                        action="store")
    parser.add_argument(
                        "-b",
                        "--make_bibtex_file",
                        dest="filename_bibtex",
                        help="Create a text file inside the target directory with name given by FILENAME_BIBTEX containing the bibtex entry of each pdf file in the target folder (if a valid identifier was found). This option is only available when a folder is targeted, and when the web validation is allowed.",
                        action="store")
    #save_identifier_metadata = config.save_identifier_metadata
    args = parser.parse_args()
    results = pdf2doi(target=args.path,
                  verbose=not(args.no_verbose),
                  websearch=not(args.no_web_search),
                  webvalidation=not(args.no_web_validation),
                  save_identifier_metadata = not(args.no_store_identifier_metadata),
                  numb_results_google_search=args.google_results,
                  filename_identifiers = args.filename_identifiers,
                  filename_bibtex = args.filename_bibtex
                  )
    if not results:
        return
    if not isinstance(results,list):
        results = [results]
    for result in results:
        if result['identifier']:
            print('{:<15s} {:<40s} {:<10s}\n'.format(result['identifier_type'], result['identifier'],result['path']) ) 

    return

if __name__ == '__main__':
    main()