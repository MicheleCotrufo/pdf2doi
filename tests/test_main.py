import logging
import os
import shlex
import subprocess
import tempfile
from pathlib import Path

import fitz
import pyperclip
import pytest

import pdf2doi
import pdf2doi.config as config

logger = logging.getLogger("pdf2doi")

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

config.update_params(default_config_params)

test_doi = r"10.1103/PhysRev.47.777".lower()
test_identifier_type = "DOI"
test_title = (
    r"Can Quantum Mechanical Description of Physical Reality Be Considered Complete"
)


@pytest.fixture
def pdf_path(tmp_path):
    file_path = tmp_path / (test_doi.replace("/", r"%2F") + " " + test_title + ".pdf")
    doc = fitz.open()
    doc.insert_page(-1, text=(test_doi + " " + test_title))
    doc.save(file_path)
    doc.close()
    return file_path


@pytest.fixture
def dir_pdfs(tmp_path):
    file_path = tmp_path / (test_title + "1.pdf")
    doc = fitz.open()
    doc.insert_page(-1, text=(test_doi + " " + test_title))
    doc.save(file_path)
    doc.close()

    file_path = tmp_path / (test_title + "2.pdf")
    doc = fitz.open()
    doc.insert_page(-1, text=(test_doi + " " + test_title))
    doc.save(file_path)
    doc.close()

    return tmp_path


def test_execution_from_cli(pdf_path):
    cmd = f'pdf2doi "{str(pdf_path)}"'
    result = subprocess.run(shlex.split(cmd), check=True, capture_output=True)

    assert result.returncode == 0

    identifier_type, identifier, *_ = result.stdout.decode().split()
    assert identifier_type == test_identifier_type
    assert identifier == test_doi


def test_optional_arguments(pdf_path):
    cmd = f'pdf2doi -v "{str(pdf_path)}"'
    result = subprocess.run(shlex.split(cmd), check=True, capture_output=True)

    assert result.returncode == 0

    identifier_type, identifier, *_ = result.stdout.decode().split()
    assert identifier_type == test_identifier_type
    assert identifier == test_doi

    verbose = result.stderr.decode().split("\n")[:-1]

    assert len(verbose)

    are_all_messages_logs = True
    for line in verbose:
        if not line.startswith("[pdf2doi]"):
            are_all_messages_logs = False
    assert are_all_messages_logs


def test_pdf2doi_singlefile(pdf_path):
    result = pdf2doi.main.pdf2doi_singlefile(pdf_path)
    assert isinstance(result, dict)
    assert result["identifier"] == test_doi
    assert result["identifier_type"] == test_identifier_type


def test_pdf2doi_directory(dir_pdfs):
    result = pdf2doi.main.pdf2doi(dir_pdfs)
    assert isinstance(result, list)
    assert len(result) == 2
    are_all_results_dicts = True
    for r in result:
        if not isinstance(r, dict):
            are_all_results_dicts = False
    assert are_all_results_dicts
    assert result[0]["identifier"] == test_doi
    assert result[0]["identifier"] == test_doi


def test_save_identifiers_to_file(dir_pdfs: Path):
    destination_filename = "dois.txt"
    cmd = f'pdf2doi -v "{str(dir_pdfs)}" -s {destination_filename}'
    result = subprocess.run(shlex.split(cmd), check=True, capture_output=True)

    assert dir_pdfs.joinpath(destination_filename).exists()


def test_save_identifiers_to_clipboard(dir_pdfs: Path):
    cmd = f'pdf2doi -v "{str(dir_pdfs)}" -clip'
    result = subprocess.run(
        shlex.split(cmd), check=True, capture_output=True, text=True
    )
    output = result.stdout.split("\n")[:-1]
    dois = []
    for line in output:
        if line:
            dois.append(line.split()[1])

    clipboard = pyperclip.paste().split("\n")[:-1]

    assert dois == clipboard
