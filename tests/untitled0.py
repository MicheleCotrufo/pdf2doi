# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 23:01:25 2021

@author: michele
"""

from pdf2doi import pdf2doi

doi = pdf2doi(file="1996 - Law, Eberly - Physical Review Letters - Arbitrary control of a quantum electromagnetic field.pdf",verbose=True)
print(doi)