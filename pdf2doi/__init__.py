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

from .main import pdf2doi
from .finders import *
from .bibtex_makers import *
from .utils_registry import install_right_click, uninstall_right_click


