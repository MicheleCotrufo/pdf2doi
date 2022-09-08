import pytest
import re
from pdf2doi.patterns import (
    doi_pattern,
    doi_regexp
)

@pytest.mark.parametrize("suspected", [
    "10.1109/sp.2011.40",
])
def test_is_strict_doi_match(suspected):
    assert re.match(doi_pattern, suspected,re.I) is not None

@pytest.mark.parametrize(["suspected", "expected"], [
    ["10.1109/sp.2011.40"] * 2,
    ["doi10.1177:0146167297234003", "10.1177:0146167297234003"],
    ["10.1177:0146167297234003.pdf", "10.1177:0146167297234003"],
])
def test_is_loose_doi_match(suspected, expected):
    print(suspected)
    for ver, regex in enumerate(doi_regexp):
        match = re.match(regex, suspected,re.I)
        if match is not None:
            assert match.group() == expected
            print(f"{ver} matched.")
            return
        print(f"{ver} failed.")
    assert False