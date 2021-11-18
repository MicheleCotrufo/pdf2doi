set path_pdf2doi=D:\Dropbox (Personal)\PythonScripts\pdf2doi\env\Scripts

REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi" /f
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi" /v "MUIVerb" /t REG_SZ /d "pdf2doi" /f
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi" /v "subcommands" /t REG_SZ /d "" /f
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell" /f

REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_doi" /t REG_SZ /d "Copy DOI/identifier of this file to clipboard..." /f
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_doi\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -clip -v" /f

REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_setdoi" /t REG_SZ /d "Specify DOI/identifier of this file..." /f
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_setdoi\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -id_input_box -v" /f

REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi" /f
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi" /v "MUIVerb" /t REG_SZ /d "pdf2doi" /f
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi" /v "subcommands" /t REG_SZ /d "" /f
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell" /f

REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell\pdf2doi_doi" /t REG_SZ /d "Retrieve and copy DOIs/identifiers of all pdf files in this folder..." /f
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell\pdf2doi_doi\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -clip -v" /f