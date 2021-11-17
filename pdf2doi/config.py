import configparser
import os
import logging

''' 
method_dxdoiorg                         It sets which method is used when querying dx.doi.org to retrieve the bibtex info
                                        Two possible values are 'text/bibliography; style=bibtex' , 'application/x-bibtex' and
                                        'application/citeproc+json'

                                        The 'application/x-bibtex' method was the one originally used in the first version of
                                        pdf2doi. However, since October 2021 this method does not return the 
                                        Journal info, as a result of a bug in dx.doi.org (Last time checked = 2021 Nov 06)
                                        I added the method 'text/bibliography; style=bibtex' to overcome this problem
                                        However, with 'text/bibliography; style=bibtex' the authors string is returned in
                                        the format "LastName1, FirstName1 SecondName1.. and LastName2, FirstName2 SecondName2.. and etc."
                                        which is not the format expect by the script pdf-renamer, which uses pdf2doi 
                                               
                                        pdf2doi automatically parses the string obtained by dx.doi.org differently based on
                                        the value of method_dxdoiorg
                                        The method "application/citeproc+json" is the best one, because it returns everythin as 
                                        a json dictionary, and it requires no parsing
check_online_to_validate

websearch

numb_results_google_search              How many results should it look into when doing a google search

N_characters_in_pdf

save_identifier_metadata                Sets the default value of the global setting save_identifier_metadata
                                        If set True, when a valid identifier is found with any method different than the metadata lookup the identifier
                                        is also written inside the file metadata with key "/identifier". If set False, this does not happen.
                                 
'''


class config():
    __params={'verbose'   :   True,
            'separator' : os.path.sep,
            'method_dxdoiorg' : 'application/citeproc+json',
            'webvalidation' : True,
            'websearch' : True,
            'numb_results_google_search' : 6,
            'N_characters_in_pdf' : 1000,
            'save_identifier_metadata' : True
            }
    __setters = __params.keys()


    @staticmethod
    def update_params(new_params):
        config.__params.update(new_params)

    @staticmethod
    def get(name):
        return config.__params[name]

    @staticmethod
    def set(name, value):
        if name in config.__setters:
             config.__params[name] = value
        else:
            raise NameError("Name not accepted in set() method")
        #Here we define additional actions to perform when specific parameters are modified
        if name == 'verbose':
            # We change the logger verbosity
            if value: loglevel = logging.INFO
            else: loglevel = logging.CRITICAL
            logger = logging.getLogger("pdf2doi")
            logger.setLevel(level=loglevel)

    @staticmethod
    def ReadParamsINIfile():
        '''
        Reads the parameters stored in the file settings.ini, and stores them in the dict self.params
        If the .ini file does not exist, it creates it with the default values.
        '''
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'settings.ini')
        if not(os.path.exists(path_config_file)):
            config.WriteParamsINIfile()
        else:
            config_object = configparser.ConfigParser()
            config_object.optionxform = str
            config_object.read(path_config_file)
            config.__params.update(dict(config_object['DEFAULT']))
            config.ConvertParamsToBool()
            config.ConvertParamsToNumb()

    @staticmethod
    def ConvertParamsToBool():
        for key,val in config.__params.items():
            if isinstance(val, str):
                if val.lower() == 'true':
                    config.__params[key]=True
                if val.lower() == 'false':
                    config.__params[key]=False

    @staticmethod
    def ConvertParamsToNumb():
        for key,val in config.__params.items():
            if isinstance(val, str) and val.isdigit():
                config.__params[key]=int(val)
    @staticmethod
    def print():
        '''
        Prints all settings
        '''
        for key,val in config.__params.items():
            print(key + " : " + str(val) + ' ('+type(val).__name__+')')

    @staticmethod
    def WriteParamsINIfile():
        '''
        Writes the parameters currently stored in in the dict self.params into the file settings.ini
        '''
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'settings.ini')
        config_object = configparser.ConfigParser()
        config_object.optionxform = str
        config_object['DEFAULT'] = config.__params
        with open(path_config_file, 'w') as configfile: #Write them on file
            config_object.write(configfile)


###########################################








