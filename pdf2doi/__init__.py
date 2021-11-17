import logging

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

config.set('verbose',config.get('verbose')) #This is a quick and dirty way (to improve in the future) to make sure that the verbosity of the pdf2doi logger is properly set according
                                            #to the current value of config.get('verbose') (see config.py file for details)
from .main import pdf2doi, pdf2doi_singlefile
from .finders import *
#from .bibtex_makers import *
from .utils_registry import install_right_click, uninstall_right_click


