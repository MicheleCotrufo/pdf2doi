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

from .pdf2doi import pdf2doi
from .finders import *
from .bibtex_makers import *


