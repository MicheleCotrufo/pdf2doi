import platform
system = platform.system()

if system.lower() == ('windows'): 
    separator = '\\'
else: 
    separator = '/'

check_online_to_validate = True
websearch = True
numb_results_google_search = 6 #How many results should it look into when doing a google search