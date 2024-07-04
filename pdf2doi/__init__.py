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


#Determine the list of libraries to be used to extract text from pdf files
reader_libraries = ['PyPdf','pdfminer'] 
# Using PyPdf before pdfminer makes sure that, in arxiv pdf files, the DOI which is sometimes written on the left margin of the first page is correctly detected

is_textract_installed = importlib.util.find_spec('textract')
if is_textract_installed:
    reader_libraries. append('textract')
    

from .main import pdf2doi, pdf2doi_singlefile
from .finders import *
#from .bibtex_makers import *
from .utils_registry import install_right_click, uninstall_right_click


