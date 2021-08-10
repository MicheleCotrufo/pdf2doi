import argparse
import logging
from os import path, listdir
import pdf2doi.finders as finders
import pdf2doi.config as config
import pyperclip

def pdf2doi(target, verbose=False, websearch=True, webvalidation=True,
            save_identifier_metadata = config.save_identifier_metadata,
            numb_results_google_search = config.numb_results_google_search,
            filename_identifiers = False, filename_bibtex = False,
            store_bibtex_clipboard = False, store_identifier_clipboard = False):
    ''' This is the main routine of the library. When the library is used as a command-line tool (via the entry-point "pdf2doi") the input arguments
    are collected, validated and sent to this function (see the function main() below).
    The function tries to extract the DOI (or other identifiers) of the publication in the pdf file whose path is specified in the input variable target. 
    If target contains the valid path of a folder, the function tries to extract the DOI/identifer of all pdf files in the folder.
    It returns a dictionary (or a list of dictionaries) containing info(s) about the file(s) examined, or None if an error occurred.
    If the input variables filename_identifiers and/or filename_bibtex are set to a valid string, all identifiers found and/or bibtex entries for
    all pdf files are saved in text files (see description of input arguments for details)

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
        inside the same directory and with a name specified by filename_identifiers. 
        The default is False.  It is ignored if the input parameter target is a file.
    filename_bibtex : string or boolean, optional
        If set equal to a string, all bibtex entries obtained in the validation process for all pdf files found in the 
        directory specified by target are saved into a file inside the same directory and with a name specified by filename_bibtex. 
        The default is False. It is ignored if the input parameter target is a file.
    store_bibtex_clipboard : boolean, optional
        If set true, the bibtex entries of all pdf files (or a for a single pdf file if target is a file) are
        stored in the system clipboard. The default is False. 
    store_identifier_clipboard : boolean, optional
        If set true, the identifier of all pdf files (or a for a single pdf file if target is a file) are
        stored in the system clipboard. The default is False. 
        If both store_bibtex_clipboard and store_identifier_clipboard are set to true, the bibtex entries have 
        priority.

    Returns
    -------
    results, dictionary or list of dictionaries (or None if an error occured)
        The output is a single dictionary if target is a file, or a list of dictionaries if target is a directory, 
        each element of the list describing one file. Each dictionary has the following keys
        
        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper. If config.check_online_to_validate = True, then result['validation_info']
                                    will typically contain a bibtex entry for this paper. Otherwise it will just contain True 
        result['bibtex_data'] = dictionary containing all available bibtex info of this publication. E.g., result['bibtex_info']['author'], result['bibtex_info']['title'], etc.
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

    #Check if path is valid
    if not(path.exists(target)):
        logger.error(f"{target} is not a valid path to a file or a directory.")
        return
      
    #Check if target is a directory
    #If yes, we look for all the .pdf files inside it, and for each of them
    #we call again this function
    if  path.isdir(target):
        logger.info(f"Looking for pdf files in the folder {target}...")
        pdf_files = [f for f in listdir(target) if (f.lower()).endswith('.pdf')]
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

        #If a string was passed via the argument filename_identifiers or if store_identifier_clipboard = True, 
        #we save all found identifiers in a either text file with name = filename_identifiers
        #and/or the system clipboard
        if isinstance(filename_identifiers,str) or store_identifier_clipboard:
            path_filename_identifiers = target+filename_identifiers if isinstance(filename_identifiers,str) else False
            save_identifiers(path_filename_identifiers, identifiers_found, store_identifier_clipboard)

                
        #If a string was passed via the argument filename_bibtex or if store_bibtex_clipboard = True, and if the online validation was used
        #we save all the bibtex entries collected during validation in either a file with name = filename_bibtex
        #and/or the system clipboard
        if (isinstance(filename_bibtex,str) or store_bibtex_clipboard) and config.check_online_to_validate:
            path_filename_bibtex = target+filename_bibtex if isinstance(filename_bibtex,str) else False
            save_bibtex(path_filename_bibtex, identifiers_found, store_bibtex_clipboard)
            
        return identifiers_found
    
    #If target is not a directory, we check that it is an existing file and that it ends with .pdf
    else:
        filename = target
        logger.info(f"Trying to retrieve a DOI/identifier for the file: {filename}")  
        if not path.exists(filename):
            logger.error(f"'{filename}' is not a valid file.")
            return None    
        if not (filename.lower()).endswith('.pdf'):
            logger.error("The file must have .pdf extension.")
            return None
        result = pdf2doi_singlefile(filename)
        if result['identifier'] == None:
            logger.error("It was not possible to find a valid identifier for this file.")

        #The next 4 lines of code need to be improved in next version. Right now, if I am scanning a folder, it will first copy
        #the details of each file separately into the clipboard, and then in the end it will copy the whole list to the clipboard
        if store_bibtex_clipboard and config.check_online_to_validate:
            save_bibtex(False, [result], store_bibtex_clipboard)
        if  store_identifier_clipboard:
            save_identifiers(False, [result], store_identifier_clipboard)

                
        return result #This will be a dictionary with all entries as None

def pdf2doi_singlefile(filename):
    ''' This function looks for an identifier of the file specified by filename
    Parameters
    ----------
    filename : string
        absolute path of a single .pdf file

    Returns
    -------
    result, dictionary
        The output is a single dictionary with the following keys
        
        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper. If config.check_online_to_validate = True, then result['validation_info']
                                    will typically contain a bibtex entry for this paper. Otherwise it will just contain True 
        result['bibtex_data'] = dictionary containing all available bibtex info of this publication. E.g., result['bibtex_info']['author'], result['bibtex_info']['title'], etc.
        result['path'] = path of the pdf file
        result['method'] = method used to find the identifier

    ''' 
    logger = logging.getLogger("pdf2doi")
    #Several methods are now applied to find a valid identifier in the .pdf file identified by filename
    
    #First method: we look into the pdf metadata (in the current implementation this is done
    # via the getDocumentInfo() method of the library PyPdf) and see if any of them is a string which containts a
    #valid identifier inside it. We first look for the elements of the dictionary with keys 'doi' or '/doi' (if the they exist), 
    #and then any other field of the dictionary 
    logger.info(f"Method #1: Looking for a valid identifier in the document infos...")
    result = finders.find_identifier(filename,method="document_infos",keysToCheckFirst=['/doi','/identfier'])
    if result['identifier']:
        return result 
        
    #Second method: We look for a DOI or arxiv ID inside the filename
    logger.info(f"Method #2: Looking for a valid identifier in the file name...")
    result = finders.find_identifier(filename,method="filename")
    if result['identifier']:
        return result 
    
    #Third method: We look in the plain text of the pdf and try to find something that matches a valid identifier. 
    logger.info(f"Method #3: Looking for a valid identifier in the document text...")
    result =  finders.find_identifier(filename,method="document_text")
    if result['identifier']:
        return result 
    
        
    #Fourth method: We look for possible titles of the paper, do a google search with them, 
    # open the first results and look for identifiers in the plain text of the searcg results.
    logger.info(f"Method #4: Looking for possible publication titles...")
    result =  finders.find_identifier(filename,method="title_google")
    if result['identifier']:
        return result
        
    #Fifth method: We extract the first N characters from the file (where N is set by config.N_characters_in_pdf) and we use it as 
    # a query for a google seaerch. We open the first results and look for identifiers in the plain text of the searcg results.
    logger.info(f"Method #5: Trying to do a google search with the first {config.N_characters_in_pdf} characters of this pdf file...")
    result =  finders.find_identifier(filename,method="first_N_characters_google")
    if result['identifier']:
        return result

    return result   #If it gets to this line, then no valid identifier was found and
                    #result is a dictionary with result['identifier'] = None 


def save_identifiers(filename_identifiers, results, clipboard = False):
    ''' Write all identifiers contained in the input list 'results' into a text file with a path specified by filename_identifiers (if filename_identifiers is a 
        valid string) and/or into the clipboard (if clipboard = True).
    
    Parameters
    ----------
    filename_identifiers : string
        Absolute path of the target file. If equal to '' or False, nothing is stored on file.
    results : list of dictionaries
        Each element of the list 'results' describes a .pdf file, and contains the pdf identifier and other infos.
    clipboard : boolean, optional
        If set to True, the identifiers are stored in the clipboard. Default is False.

    Returns
    -------
    None.
    '''
    logger = logging.getLogger("pdf2doi")
    if filename_identifiers:
        try:
            text = ''
            for result in results:
                if result['validation_info']:
                    text = text + '{:<15s} {:<40s} {:<10s}\n'.format(result['identifier_type'], result['identifier'],result['path']) 
            with open(filename_identifiers, "w", encoding="utf-8") as text_file:
                text_file.write(text) 
            logger.info(f'All found identifiers were saved in the file {filename_identifiers}')
        except Exception as e:
            logger.error(e)
            logger.error(f'A problem occurred when trying to write into the file {filename_identifiers}')
    if clipboard:
        try:
            text = ''
            for result in results:
                if result['validation_info']:
                    text = text + result['identifier'] + '\n' 
            pyperclip.copy(text)
            logger.info(f'All available identifiers have been stored in the system clipboard')
        except Exception as e:
            logger.error(e)
            logger.error(f'A problem occurred when trying to write into the system clipboard')

def save_bibtex(filename_bibtex, results, clipboard = False):
    '''Write all available bibtex entries from results contained in the input list 'results' into a text file with a path specified by filename_bibtex 
        (if filename_bibtex is a valid string) and/or into the clipboard (if clipboard = True).
    
    Parameters
    ----------
    filename_bibtex : string
        Absolute path of the target file. If equal to '' or False, nothing is stored on file.
    results : list of dictionaries
        Each element of the list 'results' describes a .pdf file, and contains the pdf identifier and other infos.
    clipboard : boolean, optional
        If set to True, the bibtex entries are stored in the clipboard. Default is False.
        
    Returns
    -------
    None.

    '''
    logger = logging.getLogger("pdf2doi")
    text = ''
    for result in results:
        if isinstance(result['validation_info'],str):
            text = text + result['validation_info'] + "\n\n"
    if filename_bibtex:
        try:
            with open(filename_bibtex, "w", encoding="utf-8") as text_file:
                text_file.write(text) 
            logger.info(f'All available bibtex entries have been stored in the file {filename_bibtex}')
        except Exception as e:
            logger.error(e)
            logger.error(f'A problem occurred when trying to write into the file {filename_bibtex}')
    if clipboard:
        try:
            pyperclip.copy(text)
            logger.info(f'All available bibtex entries have been stored in the system clipboard')
        except Exception as e:
            logger.error(e)
            logger.error(f'A problem occurred when trying to write into the system clipboard')
    
def main():
    parser = argparse.ArgumentParser( 
            description = "Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a publications.",
            epilog = "")

    parser.add_argument("path",
                        help = "Relative path of the target pdf file or of the targe folder.",
                        metavar = "path",
                        nargs = '*')
    parser.add_argument("-nv",
                        "--no_verbose",
                        help="Decrease verbosity.",
                        action="store_true")
    parser.add_argument("-nws",
                        "--no_web_search",
                        help="Disable any method to find identifiers which requires internet searches (e.g. queries to google).",
                        action="store_true")
    parser.add_argument("-nwv",
                        "--no_web_validation",
                        help="Disable the online validation of identifiers (e.g., via queries to http://dx.doi.org/).",
                        action="store_true")
    parser.add_argument("-nostore",
                        "--no_store_identifier_metadata",
                        help="By default, anytime an identifier is found it is added to the metadata of the pdf file (if not present yet). By setting this parameter, the identifier is not stored in the file metadata.",
                        action="store_true")
    parser.add_argument('-id', 
                        help=f"Stores the string IDENTIFIER in the metadata of the target pdf file, with key \'/identifier\'. Note: when this argument is passed, all other arguments (except for the path to the pdf file)" +
                            " are ignored. ",
                        action="store", dest="identifier", type=str, default=False)
    parser.add_argument("-id_input_box",#When called with this argument, an input box is generated in order
                                        #to acquire a string from the user, which is then stored in the metadata 
                                        # of the target pdf file, with key \'/identifier\'
                                        #This is normally used when calling pdf2doi by right-clicking on a
                                        #.pdf file in Windows
                        help=argparse.SUPPRESS,
                        action="store_true")
    parser.add_argument('-google_results', 
                        help=f"Set how many results should be considered when doing a google search for the DOI (default={str(config.numb_results_google_search)}).",
                        action="store", dest="google_results", type=int)
    parser.add_argument("-s",
                        "--save_identifiers_file",
                        dest="filename_identifiers",
                        help="Save all the identifiers found in the target folder in a text file inside the same folder with name specified by FILENAME_IDENTIFIERS. This option is only available when a folder is targeted.",
                        action="store")
    parser.add_argument("-b",
                        "--make_bibtex_file",
                        dest="filename_bibtex",
                        help="Create a text file inside the target directory with name given by FILENAME_BIBTEX containing the bibtex entry of each pdf file in the target folder (if a valid identifier was found). This option is only available when a folder is targeted, and when the web validation is allowed.",
                        action="store")
    parser.add_argument("-bclip",
                        "--save_bibtex_clipboard",
                        action="store_true",
                        help="Store all found bibtex entries into the clipboard.")
    parser.add_argument("-doiclip",
                        "--save_doi_clipboard",
                        action="store_true",
                        help="Store all found DOI/identifiers into the clipboard.")

    parser.add_argument("-install--right--click",
                        dest="install_right_click",
                        action="store_true",
                        help="Add a shortcut to pdf2doi in the right-click context menu of Windows. You can copy the identifier and/or bibtex entry of a pdf file (or all pdf files in a folder) into the clipboard by just right clicking on it! NOTE: this feature is only available on Windows.")
    parser.add_argument("-uninstall--right--click",
                        dest="uninstall_right_click",
                        action="store_true",
                        help="Uninstall the right-click context menu functionalities. NOTE: this feature is only available on Windows.")

    args = parser.parse_args()

    # Setup logging
    if not(args.no_verbose): loglevel = logging.INFO
    else: loglevel = logging.CRITICAL

    logger = logging.getLogger("pdf2doi")
    logger.setLevel(level=loglevel)

    #If the command -install--right--click was specified, it sets the right keys in the system registry
    if args.install_right_click:
        import pdf2doi.utils_registry as utils_registry
        utils_registry.install_right_click()
        return
    if args.uninstall_right_click:
        import pdf2doi.utils_registry as utils_registry
        utils_registry.uninstall_right_click()
        return
    if isinstance(args.path,list):
        if len(args.path)>0:
            target = args.path[0]
        else:
            target = ""
    else:
        target = args.path

    if target == "":
        print("pdf2doi: error: the following arguments are required: path. Type \'pdf2doi --h\' for a list of commands.")
        return

    #If the command -id_input_box was specified, we generate an input box, ask for a string from the user and
    #save it in args.identifier. In this way, the next if block is triggered
    if args.id_input_box:
        import easygui
        identifier = easygui.enterbox(
            f"Please specify the identifier (i.e. DOI or arxiv ID) of the file:\n '{target}' \n\n(this will be stored in the file metadata labelled '\identifier')")
        args.identifier = identifier
    #If the command -id was specified, and if the user provided a valid string, we call the sub-routine to store the string passed by the user into the metadata of the file indicated by the user
    #Nothing else will be done
    if args.identifier or args.identifier=="":
        if isinstance(args.identifier,str):
            result = finders.add_found_identifier_to_metadata(target,args.identifier)
            if args.id_input_box and len(result)>1:
                if result[0]==False:
                    easygui.msgbox(result[1])
        return

    results = pdf2doi(target=target,
                  verbose=not(args.no_verbose),
                  websearch=not(args.no_web_search),
                  webvalidation=not(args.no_web_validation),
                  save_identifier_metadata = not(args.no_store_identifier_metadata),
                  numb_results_google_search=args.google_results,
                  filename_identifiers = args.filename_identifiers,
                  filename_bibtex = args.filename_bibtex,
                  store_bibtex_clipboard = args.save_bibtex_clipboard, 
                  store_identifier_clipboard = args.save_doi_clipboard
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