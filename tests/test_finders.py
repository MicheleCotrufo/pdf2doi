import os
from pathlib import Path

import fitz
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

config.update_params(default_config_params)

valid_doi = r"10.1103/PhysRev.47.777".lower()
valid_test_title = (
    r"Can Quantum Mechanical Description of Physical Reality Be Considered Complete"
)
wrong_doi = "foo"
valid_arxiv_id = r"2407.03393"  # picked at random


@pytest.fixture
def path_to_pdf_with_valid_doi(tmp_path):
    file_path = tmp_path / (
        valid_doi.replace("/", r"%2F") + " " + valid_test_title + ".pdf"
    )
    doc = fitz.open()
    doc.insert_page(-1, text=(valid_doi + " " + valid_test_title))
    doc.save(file_path)
    doc.close()
    return file_path


@pytest.fixture
def path_to_pdf_with_valid_arxiv_id(tmp_path):
    file_path = tmp_path / (valid_arxiv_id.replace("/", r"%2F") + ".pdf")
    doc = fitz.open()
    doc.insert_page(-1, text=(valid_arxiv_id))
    doc.save(file_path)
    doc.close()
    return file_path


@pytest.fixture
def path_to_pdf_with_wrong_doi(tmp_path):
    file_path = tmp_path / (wrong_doi + ".pdf")
    doc = fitz.open()
    doc.insert_page(-1, text=(wrong_doi))
    doc.save(file_path)
    doc.close()
    return file_path


def test_validate_doi_web_with_valid_doi():
    r = pdf2doi.finders.validate_doi_web(valid_doi)
    assert isinstance(r, str)


def test_validate_doi_web_with_valid_doi_and_forced_connection_error(mocker):

    mock_get = mocker.patch("requests.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 503
    mock_get.return_value = mock_response

    r = pdf2doi.finders.validate_doi_web(valid_doi)
    assert r is None


def test_validate_doi_web_with_valid_doi_and_forced_not_found(mocker):

    mock_get = mocker.patch("requests.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 503
    mock_get.return_value = mock_response

    r = pdf2doi.finders.validate_doi_web(valid_doi)
    assert r is None


def test_validate_doi_web_with_wrong_doi():
    r = pdf2doi.finders.validate_doi_web(wrong_doi)
    assert r is None


def test_validate_arxiv_id_web_with_valid_arxiv_id():
    r = pdf2doi.finders.validate_arxivID_web(valid_arxiv_id)
    assert r is not None and r != -1


def test_validate():
    config.update_params(default_config_params)
    r = pdf2doi.finders.validate(valid_doi, what="doi")
    assert isinstance(r, str)


def test_extract_arxivID_from_text():
    r = pdf2doi.finders.extract_arxivID_from_text(valid_arxiv_id, version=2)
    assert isinstance(r, list)
    assert len(r) == 1


def test_extract_doi_from_text():
    assert pdf2doi.extract_doi_from_text(valid_doi, version=1)[0] == valid_doi


def test_find_identifier_in_google_search():

    query = valid_doi + " " + valid_test_title + ".pdf"

    identifier, desc, info = pdf2doi.find_identifier_in_google_search(
        query=query, func_validate=pdf2doi.finders.validate, numb_results=6
    )

    assert identifier == valid_doi


def test_find_identifier_in_google_search_with_mock(mocker):

    mock_search = mocker.patch("pdf2doi.finders.search")
    mock_search.return_value = [
        "https://journals.aps.org/pr/abstract/10.1103/PhysRev.47.777"
    ]

    mock_validate = mocker.patch("pdf2doi.finders.validate_doi_web")
    mock_validate.return_value = valid_doi

    # mock_get = mocker.patch('requests.get')
    # mock_response = mocker.Mock()
    # mock_response.text = valid_doi
    # mock_get.return_value = mock_response

    query = valid_doi + " " + valid_test_title + ".pdf"

    identifier, desc, info = pdf2doi.find_identifier_in_google_search(
        query=query, func_validate=pdf2doi.finders.validate, numb_results=6
    )

    mock_search.assert_called()
    # mock_get.assert_called()
    mock_search.assert_called_once_with(query, stop=6)
    # mock_get.assert_called_once_with(mock_search.return_value[0])

    assert identifier == valid_doi


def test_find_identifier_in_text():
    import string

    text = string.ascii_lowercase + valid_doi + string.ascii_uppercase
    identifier, desc, validation = pdf2doi.finders.find_identifier_in_text(
        texts=[text], func_validate=pdf2doi.finders.validate
    )
    assert identifier == valid_doi


def test_add_and_get_pdf_info(path_to_pdf_with_valid_doi):

    identifier = "test"

    assert path_to_pdf_with_valid_doi.exists()

    pdf2doi.finders.add_found_identifier_to_metadata(
        target=str(path_to_pdf_with_valid_doi), identifier=identifier
    )

    with open(path_to_pdf_with_valid_doi, "rb") as f:
        info = pdf2doi.finders.get_pdf_info(f)

    assert info is not None
    assert "/pdf2doi_identifier" in info
    assert info["/pdf2doi_identifier"] == identifier


# 1)
def test_find_identifier_in_pdf_info_with_valid_doi(path_to_pdf_with_valid_doi):

    assert path_to_pdf_with_valid_doi.exists()

    pdf2doi.finders.add_found_identifier_to_metadata(
        target=str(path_to_pdf_with_valid_doi), identifier=valid_doi
    )

    with open(path_to_pdf_with_valid_doi, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_in_pdf_info(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier == valid_doi


def test_find_identifier_in_pdf_info_with_valid_arxiv_id(
    path_to_pdf_with_valid_arxiv_id,
):

    assert path_to_pdf_with_valid_arxiv_id.exists()

    pdf2doi.finders.add_found_identifier_to_metadata(
        target=str(path_to_pdf_with_valid_arxiv_id), identifier=valid_arxiv_id
    )

    with open(path_to_pdf_with_valid_arxiv_id, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_in_pdf_info(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier == valid_arxiv_id


# 2)
def test_find_identifier_in_pdf_text(path_to_pdf_with_valid_doi):

    assert path_to_pdf_with_valid_doi.exists()

    with open(path_to_pdf_with_valid_doi, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_in_pdf_text(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier == valid_doi


def test_find_identifier_in_pdf_text_fail(path_to_pdf_with_wrong_doi):

    assert path_to_pdf_with_wrong_doi.exists()

    with open(path_to_pdf_with_wrong_doi, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_in_pdf_text(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier is None


# 3)
def test_find_identifier_in_filename(path_to_pdf_with_valid_doi):

    assert path_to_pdf_with_valid_doi.exists()

    with open(path_to_pdf_with_valid_doi, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_in_filename(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier == valid_doi


def test_find_identifier_in_filename_fail(path_to_pdf_with_wrong_doi):

    assert path_to_pdf_with_wrong_doi.exists()

    with open(path_to_pdf_with_wrong_doi, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_in_filename(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier is None


# 4)
def test_find_identifier_by_googling_title(path_to_pdf_with_valid_doi):

    assert path_to_pdf_with_valid_doi.exists()

    with open(path_to_pdf_with_valid_doi, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_by_googling_title(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier == valid_doi


def test_find_identifier_by_googling_title_fail(path_to_pdf_with_wrong_doi):

    assert path_to_pdf_with_wrong_doi.exists()

    with open(path_to_pdf_with_wrong_doi, "rb") as f:
        identifier, desc, info = pdf2doi.find_identifier_by_googling_title(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier is None


# 5)
def test_find_identifier_by_googling_first_N_characters_in_pdf(
    path_to_pdf_with_valid_doi,
):

    assert path_to_pdf_with_valid_doi.exists()

    with open(path_to_pdf_with_valid_doi, "rb") as f:
        (
            identifier,
            desc,
            info,
        ) = pdf2doi.find_identifier_by_googling_first_N_characters_in_pdf(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier == valid_doi


def test_find_identifier_by_googling_first_N_characters_in_pdf_fail(
    path_to_pdf_with_wrong_doi,
):

    assert path_to_pdf_with_wrong_doi.exists()

    with open(path_to_pdf_with_wrong_doi, "rb") as f:
        (
            identifier,
            desc,
            info,
        ) = pdf2doi.find_identifier_by_googling_first_N_characters_in_pdf(
            f, func_validate=pdf2doi.finders.validate
        )

    assert identifier is None


# extra
def test_file_size_change_after_changing_metadata(path_to_pdf_with_valid_doi: Path):

    assert path_to_pdf_with_valid_doi.exists()

    file_size_before = path_to_pdf_with_valid_doi.stat().st_size

    pdf2doi.finders.add_found_identifier_to_metadata(
        target=str(path_to_pdf_with_valid_doi), identifier=valid_doi
    )

    file_size_after = path_to_pdf_with_valid_doi.stat().st_size

    assert (file_size_after - file_size_before) < 1000


if __name__ == "__main__":
    pytest.main()
