import os

folder = 'D:\Dropbox (Personal)\PythonScripts\pdf2doi'
os.chdir(folder)

file = open("test2.pdf", 'rb') 
pdf = PdfFileReader(file,strict=False)
info = pdf.getDocumentInfo()
pageObj = pdf.getPage(0)
text = pageObj.extractText()


for url in search('Arbitrary control of a quantum electromagnetic field', stop=1):
    print(url)
    response = requests.get(url)
    data = response.text

a=extract_doi_from_text(data ,version=0)
print(a)

(a,b)=validate_doi("10.1103/PhysRevA.66.014304PACSnumber")

if(a,b):
    print(3)