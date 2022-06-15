import argparse
import logging
from os import path, listdir
import pdf2doi.finders as finders
import pdf2doi.config as config


# import easygui Modules that are commented here are imported later only when needed, to improve start up time
# import pyperclip

def pdf2doi(target):
    ''' This is the main routine of the library. When the library is used as a command-line tool (via the entry-point "pdf2doi") the input arguments
    are collected, validated and sent to this function (see the function main() below).
    The function tries to extract the DOI (or other identifiers) of the publication in the pdf files whose path is specified in the input variable target.
    If target contains the valid path of a folder, the function tries to extract the DOI/identifer of all pdf files in the folder.
    It returns a dictionary (or a list of dictionaries) containing info(s) about the file(s) examined, or None if an error occurred.

    Example:
        import pdf2doi
        path = r"Path\to\folder"
        result = pdf2doi.pdf2doi(path)
        print(result[0]['identifier'])          # Print doi/identifier of the first pdf file found in this folder
        print(result[0]['identifier_type'])     # Print the type of identifier found (e.g. 'doi' or 'arxiv')
        print(result[0]['method'])              # Print the method used to find the identifier

    Parameters
    ----------
    target : string
        Relative or absolute path of a .pdf file or a directory containing pdf files

    Returns
    -------
    results, dictionary or list of dictionaries (or None if an error occured)
        The output is a single dictionary if target is a file, or a list of dictionaries if target is a directory,
        each element of the list describing one file. Each dictionary has the following keys

        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper. If config.get('webvalidation') = True, then result['validation_info']
                                    will typically contain raw bibtex data for this paper. Otherwise it will just contain True
        result['path'] = path of the pdf file
        result['method'] = method used to find the identifier

    '''

    logger = logging.getLogger("pdf2doi")

    # Check if path is valid
    if not (path.exists(target)):
        logger.error(f"{target} is not a valid path to a file or a directory.")
        return None

    # Check if target is a directory
    # If yes, we look for all the .pdf files inside it, and for each of them
    # we call again this function
    if path.isdir(target):
        logger.info(f"Looking for pdf files in the folder {target}...")
        pdf_files = [f for f in listdir(target) if (f.lower()).endswith('.pdf')]
        numb_files = len(pdf_files)

        if numb_files == 0:
            logger.error("No pdf files found in this folder.")
            return None

        logger.info(f"Found {numb_files} pdf files.")
        if not (
        target.endswith(config.get('separator'))):  # Make sure the path ends with "\" or "/" (according to the OS)
            target = target + config.get('separator')

        identifiers_found = []  # For each pdf file in the target folder we will store a dictionary inside this list
        for f in pdf_files:
            logger.info("................")
            file = target + f
            # For each file we call again this function, but now the input argument target is set to the path of the file
            result = pdf2doi(target=file)
            logger.info(result['identifier'])
            identifiers_found.append(result)

        logger.info("................")

        return identifiers_found

    # If target is not a directory, we check that it is an existing file and that it ends with .pdf
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

        if (config.get('save_identifier_metadata')) == True:
            if result['identifier'] and not (result['method'] == "document_infos"):
                finders.add_found_identifier_to_metadata(filename, result['identifier'])

        return result  # This will be a dictionary with all entries as None


def pdf2doi_singlefile(file_path):
    ''' Try to find an identifier of the file specified by the input argument file.  This function does not check wheter filename is a valid path to a pdf file.

    Parameters
    ----------
    file : ether a string or an object file
                if it's a string, it is the absolute path of a single .pdf file

    Returns
    -------
    result, dictionary
        The output is a single dictionary with the following keys

        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper. If config.get('webvalidation') = True, then result['validation_info']
                                    will typically contain raw bibtex data for this paper. Otherwise it will just contain True
        result['path'] = path of the pdf file
        result['method'] = method used to find the identifier

    '''
    logger = logging.getLogger("pdf2doi")

    if isinstance(file_path, str):
        with open(file_path, 'rb') as file:

            # Several methods are now applied to find a valid identifier in the .pdf file identified by filename

            # First method: we look into the pdf metadata (in the current implementation this is done
            # via the getDocumentInfo() method of the library PyPdf) and see if any of them is a string which containts a
            # valid identifier inside it. We first look for the elements of the dictionary with keys '/doi' or /identifier'(if the they exist),
            # and then any other field of the dictionary
            logger.info(f"Method #1: Looking for a valid identifier in the document infos...")
            result = finders.find_identifier(file, method="document_infos", keysToCheckFirst=['/doi', '/identifier'])
            if result['identifier']:
                return result

            # Second method: We look for a DOI or arxiv ID inside the filename
            logger.info(f"Method #2: Looking for a valid identifier in the file name...")
            result = finders.find_identifier(file, method="filename")
            if result['identifier']:
                return result

            # Third method: We look in the plain text of the pdf and try to find something that matches a valid identifier.
            logger.info(f"Method #3: Looking for a valid identifier in the document text...")
            result = finders.find_identifier(file, method="document_text")
            if result['identifier']:
                return result

            # Fourth method: We look for possible titles of the paper, do a google search with them,
            # open the first results and look for identifiers in the plain text of the searcg results.
            logger.info(f"Method #4: Looking for possible publication titles...")
            result = finders.find_identifier(file, method="title_google")
            if result['identifier']:
                return result

            # Fifth method: We extract the first N characters from the file (where N is set by config.get('N_characters_in_pdf')) and we use it as
            # a query for a google seaerch. We open the first results and look for identifiers in the plain text of the searcg results.
            logger.info(
                f"Method #5: Trying to do a google search with the first {config.get('N_characters_in_pdf')} characters of this pdf file...")
            result = finders.find_identifier(file, method="first_N_characters_google")
            if result['identifier']:
                return result

    return result  # If the execution gets to this line, then no valid identifier was found and
    # result is a dictionary with result['identifier'] = None


def save_identifiers(filename_identifiers, results, clipboard=False):
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

    # If a string was passed via the args.filename_identifiers, we create the full path of the file where identifiers will be saved
    if isinstance(filename_identifiers, str):
        path_filename_identifiers = path.dirname(results[0]['path']) + config.get('separator') + filename_identifiers
        try:
            text = ''
            for result in results:
                if result['validation_info']:
                    text = text + '{:<15s} {:<40s} {:<10s}\n'.format(result['identifier_type'], result['identifier'],
                                                                     result['path'])
                else:
                    text = text + '{:<15s} {:<40s} {:<10s}\n'.format('n.a.', 'n.a.', result['path'])
            with open(path_filename_identifiers, "w", encoding="utf-8") as text_file:
                text_file.write(text)
            logger.info(f'All found identifiers were saved in the file {filename_identifiers}')
        except Exception as e:
            logger.error(e)
            logger.error(f'A problem occurred when trying to write into the file {filename_identifiers}')

    # If clipboard is set to true, we copy all identifiers into the clipboard
    if clipboard:
        import pyperclip
        try:
            text = ''
            for result in results:
                if result['validation_info']:
                    text = text + result['identifier'] + '\n'
            pyperclip.copy(text)
            logger.info(f'All found identifiers have been stored in the system clipboard')
        except Exception as e:
            logger.error(e)
            logger.error(f'A problem occurred when trying to write into the system clipboard')


def main():
    parser = argparse.ArgumentParser(
        description="Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a publications.",
        epilog="")

    parser.add_argument("path",
                        help="Relative path of the target pdf file or of the targe folder.",
                        metavar="path",
                        nargs='*')
    parser.add_argument("-v",
                        "--verbose",
                        help="Increase verbosity. By default (i.e. when not using -v), only a table with the found identifiers will be printed as output.",
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
                        help="By default, anytime an identifier is found it is added to the metadata of the pdf file (if not present yet). By using this additional option, the identifier is not stored in the file metadata.",
                        action="store_true")
    parser.add_argument('-id',
                        help=f"Stores the string IDENTIFIER in the metadata of the target pdf file, with key \'/identifier\'. Note: when this argument is passed, all other arguments (except for the path to the pdf file)" +
                             " are ignored. ",
                        action="store", dest="identifier", type=str, default=False)
    parser.add_argument("-id_input_box",  # When called with this argument, an input box is generated in order
                        # to acquire a string from the user, which is then stored in the metadata
                        # of the target pdf file, with key \'/identifier\'
                        # This is normally used when calling pdf2doi by right-clicking on a
                        # .pdf file in Windows
                        help=argparse.SUPPRESS,
                        action="store_true")
    parser.add_argument('-google',
                        help=f"Set how many results should be considered when doing a google search for the DOI (default={str(config.get('numb_results_google_search'))}).",
                        action="store", dest="google_results", type=int)
    parser.add_argument("-s",
                        "--save_identifiers_file",
                        dest="filename_identifiers",
                        help="Save all the identifiers found in the target folder in a text file inside the same folder with name specified by FILENAME_IDENTIFIERS. This option is only available when a folder is targeted.",
                        action="store")
    parser.add_argument("-clip",
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
    config.set('verbose',
               args.verbose)  # store the desired verbose level in the global config of pdf2doi. This will automatically update the logger verbosity

    # If the command -install--right--click was specified, it sets the right keys in the system registry
    if args.install_right_click:
        config.set('verbose', True)
        import pdf2doi.utils_registry as utils_registry
        utils_registry.install_right_click()
        return
    if args.uninstall_right_click:
        config.set('verbose', True)
        import pdf2doi.utils_registry as utils_registry
        utils_registry.uninstall_right_click()
        return
    if isinstance(args.path, list):
        if len(args.path) > 0:
            target = args.path[0]
        else:
            target = ""
    else:
        target = args.path

    if target == "":
        print("Error: the following arguments are required: path. Type \'pdf2doi --h\' for a list of commands.")
        return

    if not (path.exists(target)):
        print(f"Error: {target} is not a valid path to a file or a directory.")
        return None

    # If the command -id_input_box was specified, we generate an input box, ask for a string from the user and
    # save it in args.identifier. In this way, the next if block is triggered
    if args.id_input_box:
        import easygui
        identifier = easygui.enterbox(
            f"Please specify the identifier (i.e. DOI or arxiv ID) of the file:\n '{target}' \n\n(this will be stored in the file metadata labelled '\identifier')")
        args.identifier = identifier
    # If the command -id was specified, and if the user provided a valid string, we call the sub-routine to store the string passed by the user into the metadata of the file indicated by the user
    # Nothing else will be done
    if args.identifier or args.identifier == "":
        if isinstance(args.identifier, str):
            result = finders.add_found_identifier_to_metadata(target, args.identifier)
            if args.id_input_box and len(result) > 1:
                if result[0] == False:
                    easygui.msgbox(result[1])
        return

    config.set('websearch', not (args.no_web_search))
    config.set('webvalidation', not (args.no_web_validation))
    config.set('save_identifier_metadata', not (args.no_store_identifier_metadata))

    if args.google_results:
        config.set('numb_results_google_search', args.google_results)
    results = pdf2doi(target=target)

    if not results:
        return
    if not isinstance(results, list):
        results = [results]
    for result in results:
        if result['identifier']:
            print('{:<15s} {:<40s} {:<10s}\n'.format(result['identifier_type'], result['identifier'], result['path']))
        else:
            print('{:<15s} {:<40s} {:<10s}\n'.format('n.a.', 'n.a.', result['path']))

            # Call the function save_identifiers. If args.filename_identifiers is a valid string, it will save all found identifiers in a text file with that name.
    # If args.save_doi_clipboard is true, it will copy all identifiers into the clipboard. Otherwise, it will do nothing
    save_identifiers(args.filename_identifiers, results, args.save_doi_clipboard)

    return


if __name__ == '__main__':
    main()