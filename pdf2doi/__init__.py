import logging
import importlib.util

# Setup logging
logger = logging.getLogger("pdf2doi")
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("[pdf2doi]: %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.propagate = False

from .config import config
config.ReadParamsINIfile()  #Load all current configuration from the .ini file. If the .ini file is not present, it generates it using default values

#Determine the list of libraries to be used to extract text from pdf files
reader_libraries = ['PyPdf','pdfminer'] 
# Using PyPdf before pdfminer makes sure that, in arxiv pdf files, the DOI which is sometimes written on the left margin of the first page is correctly detected

is_textract_installed = importlib.util.find_spec('textract')
if is_textract_installed:
    reader_libraries. append('textract')
    

config.set('verbose',config.get('verbose')) #This is a quick and dirty way (to improve in the future) to make sure that the verbosity of the pdf2doi logger is properly set according
                                            #to the current value of config.get('verbose') (see config.py file for details)
from .main import pdf2doi, pdf2doi_singlefile
from .finders import *
#from .bibtex_makers import *
from .utils_registry import install_right_click, uninstall_right_click


