set path_pdf2doi=D:\Dropbox (Personal)\PythonScripts\env\Scripts


REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi"
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi" /v "MUIVerb" /t REG_SZ /d "pdf2doi"
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi" /v "subcommands" /t REG_SZ /d ""
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell"

REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_bibtex" /t REG_SZ /d "Copy BibTeX entry to clipboard..."
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_bibtex\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -bclip"

REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_doi" /t REG_SZ /d "Copy DOI/identifier to clipboard..."
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_doi\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -doiclip"

REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_setdoi" /t REG_SZ /d "Specify DOI/identifier of this file..."
REG ADD "HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_setdoi\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -id_input_box"

REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi"
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi" /v "MUIVerb" /t REG_SZ /d "pdf2doi"
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi" /v "subcommands" /t REG_SZ /d ""
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell"

REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell\pdf2doi_bibtex" /t REG_SZ /d "Copy BibTeX entry to clipboard..."
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell\pdf2doi_bibtex\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -bclip"

REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell\pdf2doi_doi" /t REG_SZ /d "Copy DOI/identifier to clipboard..."
REG ADD "HKEY_CLASSES_ROOT\Directory\shell\pdf2doi\shell\pdf2doi_doi\command" /t REG_SZ /d "%path_pdf2doi%\pdf2doi.exe \"%%1\" -doiclip"