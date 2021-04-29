import platform
system = platform.system()

if system.lower() == ('windows'): 
    separator = '\\'
else: 
    separator = '/'

check_online_to_validate = True
websearch = True
numb_results_google_search = 6 #How many results should it look into when doing a google search
N_characters_in_pdf = 1000
save_identifier_metadata = True #Sets the default value of the global setting save_identifier_metadata
                                #If set True, when a valid identifier is found with any method different than the metadata lookup the identifier
                                #is also written inside the file metadata with key "/identifier". If set False, this does not happen.
                                 