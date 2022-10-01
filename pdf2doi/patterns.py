# This regex for the DOI is taken from https://www.crossref.org/blog/dois-and-matching-regular-expressions/
# but allows multiple separator types, a prefix, and assumes the DOI is lowercase.
import re

# Based on local DOI corpus:
# 0% have non-standard separators (e.g. 10.1177:0146167297234003)
# 0.0009% have a non-standard namespace (i.e. not \d{4,9}), all match [\d\.]{1,15}
# 32% have interesting characters (i.e. not [.\/a-z0-9])
# 99.34% match this pattern: '^10\.\d{4,9}/[-._;()\/:a-z0-9][a-z0-9]$'
# 99.43% match this pattern: '^10\.\d{4,9}/[-._;()\/:a-z0-9]+$', crossref claim 99.3%
# 99.880% terminate in alphanumeric characters [a-z0-9]
# 99.804% match: ^10[.][\d.]{1,15}/[-._;:()/a-z0-9<>]+[a-z0-9]$
# 99.9999% match: ^10[.][\d.]{1,15}/[-._;()/:a-z0-9<>@\]\[#+?\s&]+$
DOI = r"""(?xm)
  (?P<marker>   doi[:\/\s]{0,3})?
  (?P<prefix>
    (?P<namespace> 10)
    [.]
    (?P<registrant> \d{2,9})
  )
  (?P<sep>     [:\-\/\s\]])
  (?P<suffix>  [\-._;()\/:a-z0-9]+[a-z0-9]) 
  (?P<trailing> ([\s\n\"<.]|$))
"""

def standardise_doi(identifier):
    """
    Standardise a DOI by removing any marker, lowercase, and applying a consistent separator
    """
    doi_meta = dict()
    for match in re.finditer(DOI, identifier.lower()):
        doi_meta.update(match.groupdict())
    
    if any(key not in doi_meta for key in ["registrant", "suffix"]):
        return None
    
    return f"10.{doi_meta['registrant']}/{doi_meta['suffix']}"


# This is a regex for arxiv identifiers (in use after 2007) and it is used to validate a given arxiv ID.
arxiv2007_pattern = '^(\d{4}\.\d+)(?:v\d+)?$'
                                                                            

# The list doi_regexp contains several regular expressions used to identify a DOI in a string. They are (roughly) ordered from stricter to less and less strict.
doi_regexp = ['doi[\s\.\:]{0,2}(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n\"<]|$)', # version 0 looks for something like "DOI : 10.xxxxS[end characters] where xxxx=4 digits, S=combination of characters, digits, ., :, -, and / of any length
                                                                            # [end characters] is either a space, newline, " , < or the end of the string. The initial part could be either "DOI : ", "DOI", "DOI:", "DOI.:", ""DOI:." 
                                                                            # and with possible spaces or lower cases.
              '(10\.\d{4}[\d\:\.\-\/a-z]+)(?:[\s\n\"<]|$)',                 # in version 1 the requirement of having "DOI : " in the beginning is removed
              '(10\.\d{4}[\:\.\-\/a-z]+[\:\.\-\d]+)(?:[\s\na-z\"<]|$)',     # version 2 is useful for cases in which, in plain texts, the DOI is not followed by a space, newline or special characters,
                                                                            #but is instead followed by other letters. In this case we can still isolate the DOI if we assume that the DOI always ends with numbers
              'https?://[ -~]*doi[ -~]*/(10\.\d{4,9}/[-._;()/:a-z0-9]+)(?:[\s\n\"<]|$)', # version 3 is useful when the DOI can be found in a google result as an URL of the form https://doi.org/[DOI]
                                                                            #The regex for [DOI] is 10\.\d{4,9}/[-._;()/:a-z0-9]+ (taken from here https://www.crossref.org/blog/dois-and-matching-regular-expressions/)
                                                                            #and it must be followed by a valid ending character: either a speace, a new line, a ", a <, or end of string.
              '^(10\.\d{4,9}/[-._;()/:a-z0-9]+)$']                         # version 4 is like version 3, but without the requirement of the url https://doi.org/ in front of it.
                                                                            #However, it requires that the string contains ONLY the doi and nothing else. This is useful for when the DOI is stored in metadata

             
#Similarly, arxiv_regexp is a list of regular expressions used to identify an arXiv identifier in a string. They are (roughly) ordered from stricter to less and less strict. Moreover,
#the regexp corresponding to older arXiv notations have less priority.
#NOTE: currently only one regexp is implemented for arxiv. 
arxiv_regexp = ['arxiv[\s]*\:[\s]*(\d{4}\.\d+)(?:v\d+)?(?:[\s\n\"<]|$)',  #version 0 looks for something like "arXiv:YYMM.number(vn)" 
                                                                            #where YYMM are 4 digits, numbers are up to 5 digits and (vn) is
                                                                            #an additional optional term specifying the version. n is an integer starting from 1
                                                                            #This is the official format for Arxiv indentifier starting from 1 April 2007
                                                                            #This is the official format for Arxiv indentifier starting from 1 April 2007
                '(\d{4}\.\d+)(?:v\d+)?(?:\.pdf)',                         #version 1 is similar to version 0, without the requirement of "arxiv : " at the beginning 
                                                                            #but with the requirement that '.pdf' appears right after the possible arXiv identifier. 
                                                                            #This is helpful when we are trying to extrat the arXiv ID from the file name.
                '^(\d{4}\.\d+)(?:v\d+)?$']                               #version 2 is similar to version 0, without the requirement of "arxiv : " at the beginning 
                                                                            #but requires that the string contains ONLY the arXiv ID.
