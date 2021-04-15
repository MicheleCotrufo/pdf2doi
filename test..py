import sys
#sys.path.append("./")
from PyPDF2 import PdfFileReader
import pdf2doi
import logging



pdf2doi.check_online_to_validate = False

print(pdf2doi.check_online_to_validate_doi)
pdf2doi.check_online_to_validate_doi = False
print(pdf2doi.check_online_to_validate_doi)

text = pdf2doi.getPDFContent('./arxiv/1901.03705.pdf', reader='textract')

# from importlib import reload  # Not needed in Python 2
# reload(logging)

# # Setup logging
# loglevel = logging.INFO
# logging.basicConfig(format="%(message)s", level=loglevel)


file = open('./arxiv/1901.03705.pdf', 'rb') 


pdf = PdfFileReader('./arxiv/1901.03705.pdf',strict=False)
info = pdf.getDocumentInfo()
pdf.close()

pageObj = pdf.getPage(3)
text = pageObj.extractText()
pdf2doi.extract_arxivID_from_text(text,version=0)

# doi = pdf2doi.find_doi_in_pdf_info(pdf,keys=['/doi','doi'])
# #doi = pdf2doi.find_doi_in_pdf_info(pdf)
# print(doi)

info = pdf2doi.get_pdf_info('./arxiv/1901.03705.pdf')

doi = pdf2doi.pdf2doi('./examples/1901.03705.pdf',verbose=True,webvalidation=True)
print(doi)

doi = pdf2doi.pdf2doi('./examples/1901.04129.pdf',verbose=True)
print(doi)

result = pdf2doi.arxiv2bib("1901.04129")

pdf2doi.doi2bib("10.1063/PT.3.4111")

doi = pdf2doi.pdf2doi('./arxiv/1901.04439.pdf',verbose=True)
print(doi)


r=pdf2doi.arxiv2bib('1901.04129')
print(r)
items = r.entries
found = len(items) > 0

filename = './arxiv/1901.03705.pdf'
import textract
text = textract.process('./arxiv/1901.03705.pdf')
texts = pdf2doi.getPDFContent(filename,'textract')
len(texts)