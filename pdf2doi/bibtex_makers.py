import requests
import feedparser
import re
import logging
logger = logging.getLogger('pdf2doi')

def doi2bib(doi):
    """
    Return a bibTeX string of metadata for a given DOI.
    """
    try:
        url = "http://dx.doi.org/" + doi
        headers = {"accept": "application/x-bibtex"}
        NumberAttempts = 10
        while NumberAttempts:
            r = requests.get(url, headers = headers)
            text = r.text
            if (text.lower().find("503 Service Unavailable".lower() )>=0) or (not text):
                
                NumberAttempts = NumberAttempts -1
                logging.info("Could not reach dx.doi.org. Trying again. Attempts left: " + str(NumberAttempts))
                continue
            else:
                NumberAttempts = 0
                
            if (text.lower().find( "DOI Not Found".lower() ))==-1:
                return text
            else:
                return None
    except Exception as e:
        logger.error(e)
        return -1

def arxiv2bib(arxivID):
    """
    Return a bibTeX string of metadata for a given arxiv ID, or None if the arxiv ID is not valid.
    """
    try:
        url = "http://export.arxiv.org/api/query?search_query=id:" + arxivID
        result = feedparser.parse(url)
        items = result.entries[0]
        found = len(items) > 0
        if not found: return None
        
        #Extract data
        data_to_extract = ['title','authors','author','link','published','arxiv_doi']
        data =[items[key] if key in items.keys() else None for key in data_to_extract]
        data_dict = dict(zip(data_to_extract,data))
        data_dict['eprint'] ="arXiv:" + arxivID 
        data_dict['ejournal'] ="arXiv" 
        
        #rename some of the keys to match the bibtex standards
        data_dict['url'] = data_dict.pop('link')
        data_dict['doi'] = data_dict.pop('arxiv_doi')
        
        #get the first word of title (for the bibtex ID)
        if data_dict['title']:
            FirstWordTitle = data_dict['title'].split()[0]
        else:
            FirstWordTitle = ""
        
        #parse the published data to get the year, month and day
        if data_dict['published']:
            regexDate = re.search('(\d{4}\-\d{2}\-\d{2})',data_dict['published'],re.I)
            if regexDate:
                date_list =  (regexDate.group(1)).split("-")
                year = date_list[0] if len(date_list)>0 else '0000'
                month = date_list[1] if len(date_list)>1 else '00'
                day = date_list[2] if len(date_list)>2 else '00'
        else:
            year = '0000'
            month = '00'
            day = '00'
        data_dict['year'] = year
        data_dict['month'] = month
        data_dict['day'] = day
        
        #if authors are defined as list, create a string out of it. We also extract the last name
        #of first author for later use
        if data_dict['authors'] and isinstance(data_dict['authors'],list):
            authors = [author['name'] for author in data_dict['authors']]
            LastNameFirstAuthor = (authors[0].split())[-1]
            authors_string = " and ".join(authors)
            data_dict['authors'] = authors_string
        elif data_dict['authors']:
            LastNameFirstAuthor = (data_dict['authors'].split())[-1]
        else:
            LastNameFirstAuthor =  arxivID #If for some reason we cant find last name of an author, we use the arxiv ID instead
        data_dict['id'] = year + "_" + LastNameFirstAuthor + "_" + FirstWordTitle
        return make_bibtex(data_dict) 
    except Exception as e:
        logger.error(e)
        return None

def make_bibtex(data):
    text = ["@article{" + data['id']]
    for key, value in data.items():
        if value:
            text.append("\t%s = {%s}" % (key, value))

    return (",\n").join(text) + "\n" + "}"
