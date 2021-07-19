'''
This module contains functions that are used to add or remove keys to the registry of Windows, for the purposes
of accessing pdf2doi by right clicking on a file or a directory
'''

import logging
from sys import executable as python_path
from os import path
import os

if os.name == 'nt':
    import winreg as reg

logger = logging.getLogger("pdf2doi")

#def create_registry_key_rightclick_menu(key,registry_title, title, command):
    
#    k1 = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key, 0, winreg.KEY_SET_VALUE)
#    #k1 = winreg.CreateKey(reg, filetype) 
#    k2 = winreg.CreateKey(k1, "shell")
#    k3 = winreg.CreateKey(k2, registry_title)
#    namekey1 = "HKEY_CLASSES_ROOT\\" + key + "\\shell\\" + registry_title
#    if title != None:
#        winreg.SetValueEx(k3, None, 0, winreg.REG_SZ, title)
#    logger.info("Created the key \"%s\" with value \"%s\"" % (namekey1,str(title)))
#    k4 = winreg.CreateKey(k3, "command")
#    winreg.SetValueEx(k4, None, 0, winreg.REG_SZ, command)
#    logger.info("Created the key \"%s\" with value \"%s\"" % (namekey1 + "\\command",command))
#    winreg.CloseKey(k3)
#    winreg.CloseKey(k2)
#    winreg.CloseKey(k1)
#    #winreg.CloseKey(reg)

def delete_sub_key(key0, current_key, arch_key=0):
    #Code inpsired by Orsiris de Jong's solution https://stackoverflow.com/questions/38205784/python-how-to-delete-registry-key-and-subkeys-from-hklm-getting-error-5
    open_key = reg.OpenKey(key0, current_key, 0, reg.KEY_ALL_ACCESS | arch_key)
    info_key = reg.QueryInfoKey(open_key)
    for x in range(0, info_key[0]):
        # NOTE:: This code is to delete the key and all sub_keys.
        # If you just want to walk through them, then
        # you should pass x to EnumKey. sub_key = reg.EnumKey(open_key, x)
        # Deleting the sub_key will change the sub_key count used by EnumKey.
        # We must always pass 0 to EnumKey so we
        # always get back the new first sub_key.
        sub_key =reg.EnumKey(open_key, 0)
        try:
            reg.DeleteKey(open_key, sub_key)
            logger.info("Removed %s\\%s " % (current_key, sub_key))
        except OSError:
            delete_sub_key(key0, "\\".join([current_key,sub_key]), arch_key)
            # No extra delete here since each call
            # to delete_sub_key will try to delete itself when its empty.

    reg.DeleteKey(open_key, "")
    open_key.Close()
    logger.info("Removed %s" % current_key)
    return

def install_right_click():
    if not(os.name == 'nt'):
        logger.error(f'This functionality is currently implemented only for Windows.')
        return
    python_folder = path.dirname(python_path)
    if python_folder[-7:].lower() == 'scripts': #This typically happens when python is installed in a virtual environment
        path_pdf2doi = python_folder + "\pdf2doi.exe"
    else:
        path_pdf2doi = python_folder + "\scripts\pdf2doi.exe"
    logger.info(f'Adding pdf2doi to the right-click context menu by adding keys to the system register...')
    try:

        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'Directory\shell\pdf2doi')
        reg.SetValueEx(key, 'MUIVerb', 0, reg.REG_SZ, 'pdf2doi')
        reg.SetValueEx(key, 'subcommands', 0, reg.REG_SZ, '')
        reg.CloseKey(key)
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'Directory\shell\pdf2doi\shell')
        reg.CloseKey(key)

        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'Directory\shell\pdf2doi\shell\pdf2doi_bibtex')
        reg.SetValue(key, '', reg.REG_SZ, 'Retrieve and copy BibTeX entries of all pdf files in this folder...')
        reg.CloseKey(key)
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'Directory\shell\pdf2doi\shell\pdf2doi_bibtex\command')
        reg.SetValue(key, '', reg.REG_SZ, path_pdf2doi + " \"%1\" -bclip")
        reg.CloseKey(key)

        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'Directory\shell\pdf2doi\shell\pdf2doi_doi')
        reg.SetValue(key, '', reg.REG_SZ, 'Retrieve and copy DOIs/identifiers of all pdf files in this folder...')
        reg.CloseKey(key)
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'Directory\shell\pdf2doi\shell\pdf2doi_doi\command')
        reg.SetValue(key, '', reg.REG_SZ, path_pdf2doi + " \"%1\" -doiclip")
        reg.CloseKey(key)


        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi')
        reg.SetValueEx(key, 'MUIVerb', 0, reg.REG_SZ, 'pdf2doi')
        reg.SetValueEx(key, 'subcommands', 0, reg.REG_SZ, '')
        reg.CloseKey(key)
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi\shell')
        reg.CloseKey(key)

        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_bibtex')
        reg.SetValue(key, '', reg.REG_SZ, 'Copy BibTeX entry to clipboard...')
        reg.CloseKey(key)
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_bibtex\command')
        reg.SetValue(key, '', reg.REG_SZ, path_pdf2doi + " \"%1\" -bclip")
        reg.CloseKey(key)

        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_doi')
        reg.SetValue(key, '', reg.REG_SZ, 'Copy DOI/identifier to clipboard...')
        reg.CloseKey(key)
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_doi\command')
        reg.SetValue(key, '', reg.REG_SZ, path_pdf2doi + " \"%1\" -doiclip")
        reg.CloseKey(key)

        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_setdoi')
        reg.SetValue(key, '', reg.REG_SZ, 'Specify DOI/identifier of this file...')
        reg.CloseKey(key)
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, 'SystemFileAssociations\.pdf\shell\pdf2doi\shell\pdf2doi_setdoi\command')
        reg.SetValue(key, '', reg.REG_SZ, path_pdf2doi + " \"%1\" -id_input_box")
        reg.CloseKey(key)

        #create_registry_key_rightclick_menu(key="SystemFileAssociations\\.pdf",registry_title="pdf2doi_bibtex", 
        #                                    title="Copy BibTeX entry to clipboard...", command=path_pdf2doi + " \"%1\" -bclip" )
        #create_registry_key_rightclick_menu(key="SystemFileAssociations\\.pdf",registry_title="pdf2doi_doi", 
        #                                    title="Copy DOI/identifier to clipboard...", command=path_pdf2doi + " \"%1\" -doiclip" )
        #create_registry_key_rightclick_menu(key="SystemFileAssociations\\.pdf",registry_title="pdf2doi_setdoi", 
        #                                    title="Specify DOI/identifier of this file...", command=path_pdf2doi + " \"%1\" -id_input_box" )
        #create_registry_key_rightclick_menu(key="Directory",registry_title="pdf2doi_bibtex", 
        #                                    title="Retrieve and copy BibTeX entries of all pdf files in this folder...", command=path_pdf2doi + " \"%1\" -bclip" )
        #create_registry_key_rightclick_menu(key="Directory",registry_title="pdf2doi_doi", 
        #                                    title="Retrieve and copy DOIs/identifiers of all pdf files in this folder...", command=path_pdf2doi + " \"%1\" -doiclip" )
        #create_registry_key_rightclick_menu(key="Directory",registry_title="pdf2doi", 
        #                                    title="Retrieve and copy BibTeX entries of all pdf files in this folder...", command=path_pdf2doi + " \"%1\" -bclip" )
        logger.info(f'All necessary keys were added to the system register.')
    except Exception as e:
        logger.error(e)
        logger.error(f'A problem occurred when trying to add pdf2doi to the right-click context menu.\nNOTE: this functionality is only available in Windows, and it has to be installed from a terminal with administrator rights.')
 
def uninstall_right_click():
    if not(os.name == 'nt'):
        logger.error(f'This functionality is currently implemented only for Windows.')
        return
    logger.info(f'Removing all keys associated to pdf2doi from the system register...')
    try:
        #delete_sub_key(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\.pdf\shell\pdf2doi_bibtex")
        #delete_sub_key(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\.pdf\shell\pdf2doi_doi")
        #delete_sub_key(winreg.HKEY_CLASSES_ROOT, "SystemFileAssociations\.pdf\shell\pdf2doi_setdoi")
        #delete_sub_key(winreg.HKEY_CLASSES_ROOT, "Directory\shell\pdf2doi_bibtex")
        delete_sub_key(reg.HKEY_CLASSES_ROOT, "SystemFileAssociations\.pdf\shell\pdf2doi")
        delete_sub_key(reg.HKEY_CLASSES_ROOT, "Directory\shell\pdf2doi")
        logger.info(f'All keys were removed.')
    except Exception as e:
        logger.error(e)
        logger.error(f'A problem occurred when trying to remove keys from the system registry.\nNOTE: this command needs to be executed from a terminal with administrator rights.')
 
