import os

import pytest

import pdf2doi
import pdf2doi.config as config

default_config_params = {
    "verbose": True,
    "separator": os.path.sep,
    "method_dxdoiorg": "application/citeproc+json",
    "webvalidation": True,
    "websearch": True,
    "numb_results_google_search": 6,
    "N_characters_in_pdf": 1000,
    "save_identifier_metadata": True,
    "replace_arxivID_by_DOI_when_available": True,
}


def test_config():
    config.update_params(default_config_params)
    for k in default_config_params:
        config.set(k, default_config_params[k])

# this test actually changes the settings file used by the tool
# this change should be either mocker, or restored, or applied to a temporary file
# it would require the read and write functions to be edited so they accept a path for settings file
# def test_read_write_config():
#     new_params = {
#         "verbose": False,
#         "separator": os.path.sep,
#         "method_dxdoiorg": "application/citeproc+json",
#         "webvalidation": False,
#         "websearch": False,
#         "numb_results_google_search": 10,
#         "N_characters_in_pdf": 100,
#         "save_identifier_metadata": False,
#         "replace_arxivID_by_DOI_when_available": False,
#     }
#     config.update_params(new_params)
#     config.WriteParamsINIfile()
#     config.update_params(default_config_params)
#     config.ReadParamsINIfile()
#     for k in new_params:
#         config.set(k, new_params[k])
