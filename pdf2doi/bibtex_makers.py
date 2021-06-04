import requests
import feedparser
import re
import logging
import urllib.parse
from unidecode import unidecode
import bibtexparser

logger = logging.getLogger('pdf2doi')


def doi2bib(doi):
    """
    Return a a bibTeX entry for a given DOI. 
    It returns None if no data was found for this DOI, or -1 if it was not possible to connect to dx.doi.org
    """
    try:
        url = "http://dx.doi.org/" + doi
        headers = {"accept": "application/x-bibtex"}
        NumberAttempts = 10
        while NumberAttempts:
            r = requests.get(url, headers = headers)
            r.encoding = 'utf-8' #This forces to encode the obtained text with utf-8
            text = r.text
            if (text.lower().find("503 Service Unavailable".lower() )>=0) or (not text):
                NumberAttempts = NumberAttempts -1
                logging.info("Could not reach dx.doi.org. Trying again. Attempts left: " + str(NumberAttempts))
                continue
            else:
                NumberAttempts = 0
            if (text.lower().find( "DOI Not Found".lower() ))==-1:
                #If a valid bibtex string was returned by dx.doi.org, we use it to generate a bibtex entry in the desired format.
                #The string returned by dx.doi.org is normally already in a decent bibtex format.
                #However, we want to do some small changes, such as the format of the ID, and replace any non-ascii character 
                #by the corresponding latex escaper. To do so, we first parse the bibtex data by
                #using the bibtexparser module, which creates a dictionary.
                #We then pass this dictionary to the function make_bibtex to ressemble the bibtex entry
                data = bibtexparser.loads(text)
                metadata = data.entries[0]
                return make_bibtex(metadata)
            else:
                return None
    except Exception as e:
        logger.error(r"Some error occured within the function doi2bib")
        logger.error(e)
        return -1

def arxiv2bib(arxivID):
    """
    Return a bibTeX entry for a given arxiv ID.
    It returns None if no data was found for this arxiv ID, or -1 if it was not possible to connect to export.arxiv.org.
    """
    try:
        url = "http://export.arxiv.org/api/query?search_query=id:" + arxivID
        result = feedparser.parse(url)
        items = result.entries[0]
        found = len(items) > 0
        if not found: return None
        
        #Extract data from the dictionary items
        data_to_extract = ['title','authors','author','link','published','arxiv_doi']
        data =[items[key] if key in items.keys() else None for key in data_to_extract]

        #Create the dictionary data_dict which will be passed to the function make_bibtex
        data_dict = dict(zip(data_to_extract,data))

        #add additionaly values
        data_dict['eprint'] ="arXiv:" + arxivID 
        data_dict['ejournal'] ="arXiv" 
        data_dict['ENTRYTYPE'] = 'article'
        #rename some of the keys in order to match the bibtex standards
        data_dict['url'] = data_dict.pop('link')
        data_dict['doi'] = data_dict.pop('arxiv_doi')       
        #parse the published data to get the year, month and day
        if data_dict['published']:
            regexDate = re.search('(\d{4}\-\d{2}\-\d{2})',data_dict['published'],re.I)
            if regexDate:
                date_list =  (regexDate.group(1)).split("-")
                year = date_list[0] if len(date_list)>0 else '0000'
                month = date_list[1] if len(date_list)>1 else '00'
                day = date_list[2] if len(date_list)>2 else '00'
        else:
            year,month,day = '0000', '00', '00'
        data_dict['year'] = year
        data_dict['month'] = month
        data_dict['day'] = day

        if 'authors' in data_dict:
            authors = data_dict['authors']
        elif 'author' in data_dict:
            authors = data_dict['author']
        else:
            authors = ''
        
        #if authors are defined as list, create a string out of it, with the format 
        #"Name1 Lastname1 and Name2 Lastname2 and ... "
        if authors and isinstance(authors,list):
            authorsnames_list = [author['name'] for author in authors]
            data_dict['authors'] = " and ".join(authorsnames_list)

        return make_bibtex(data_dict) 
    except Exception as e:
        logger.error(e)
        return None

def remove_latex_codes(text):
    #It replaces any latex special code (e.g. {\`{u}}) by the "closest" unicode character (e.g. u). This is useful when
    #certain strings which might contain latex codes need to be use in contexts where only unicode characters are accepted
    
    #This regex looks for any substring that matched the pattern "{\string1{string2}}" where string1 can be anything,
    #and it replaces the whole substring by string2
    text_sanitized = re.sub(r"{\\.+{([\w]+)}}", r"\1", text)
    return text_sanitized

def make_bibtex(data):
    #Based on the metadata contained in the input dictionary data, it creates a valid bibtex entry
    #The name of the entry has the format [lastname_firstauthor][year][first_word_title] all in lowe case
    #If the tag url is present, any possible ascii code (e.g. %2f) is decoded
    #Note: the code below assumes that the string of the authors has the format "Name1 Lastname1 and Name2 Lastname2 and ... "
    #This is normally the format returned by dx.doi.org

    #Generate the ID by looking for last name of firs author, year of publicaton, and first word of title
    if 'authors' in data.keys():
        author_string = data['authors']
    elif 'author' in data.keys():
        author_string = data['author']
    else:
        author_string = ''
    if author_string:
        firstauthor = author_string.split('and')[0]
        lastname_firstauthor = (firstauthor.strip()).split(' ')[-1]
    else: 
        lastname_firstauthor = ''
    year = data['year'] if 'year' in data.keys() else ''
    first_word_title =  data['title'].split(' ')[0] if 'title' in data.keys() else ''
    id = lastname_firstauthor + year + first_word_title
    id = id.lower()
    id = remove_latex_codes(id)
    id = unidecode(id) #This makes sure that the id of the bibtex entry is only made out of ascii characters (i.e. no accents, tildes, etc.)
    if id == '':
        id = 'NoValidID'

    #Sanitize the URL
    if 'url' in data.keys():
        data['url'] = urllib.parse.unquote(data['url'])

    if not 'ENTRYTYPE' in data.keys():
        data['ENTRYTYPE'] = 'article'

    #Create the entry
    metadata_not_to_use = ['ENTRYTYPE','ID'] #These are temporary metadata, not useful for bibtex
    text = ["@"+data['ENTRYTYPE']+"{" + id]
    for key, value in data.items():
        if value and not (key in metadata_not_to_use):
            text.append("\t%s = {%s}" % (key, value))
    bibtex_entry = (",\n").join(text) + "\n" + "}"
    return bibtex_entry
