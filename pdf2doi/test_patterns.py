import pytest
import re
from pdf2doi.patterns import (
    doi_regexp,
    standardise_doi
)

BASIC_DOIS = [
    "10.1006/jmrb.1993.1004",
    "10.1068/p080244",
    "10.2307/357448",
    "10.1002/cber.19260590832",
    "10.1016/0141-4607(85)90047-2",
    "10.1016/j.gaitpost.2009.07.035",
    "10.1109/sibgrapi.2012.5",
    "10.1111/j.1532-5415.2012.04014.x",
    "10.2307/3950104",
    "10.1002/esp.3322"
]

DOIS_WITH_NON_STANDARD_SEPARTORS = [
    doi.replace("/", ":") for doi in BASIC_DOIS
] + [
    doi.replace("/", " ") for doi in BASIC_DOIS
] + [
    f"[{doi.replace('/', ']')}" for doi in BASIC_DOIS
]

# Also includes those with dots
DOIS_WITH_SHORT_NAMESPACES = [
    "10.2.337/dc08-2337",
    "10.58.12/numonthly.14189",
    "10.16/j.reuma.2008.12.011"
]

# Note that these are NOT supported, but useful to collate in future versions
STRANGE_BUT_VALID_DOIS = [
    "10.1642/0004-8038(2005)122[0121:POTPIS]2.0.CO;2",
    "10.1002/1521-4141(200106)31:6<1685::aid-immu1685>3.0.co;2-v",
    "10.1676/0043-5643(2002)114[0197:rbacib]2.0.co;2",
    "10.1061/(asce)0733-9429(2008)134:4(390)" # terminates in a closing parenthesis
]

@pytest.mark.parametrize(["suspected", "expected"], [
    ["10.1177:0146167297234003", "10.1177/0146167297234003"],
    ["10.1109/CVPR.2016.90.", "10.1109/cvpr.2016.90"],
    *zip(DOIS_WITH_NON_STANDARD_SEPARTORS, BASIC_DOIS + BASIC_DOIS + BASIC_DOIS)
])
def test_standardise_doi(suspected, expected): 
    assert standardise_doi(suspected) == expected

@pytest.mark.parametrize(["suspected", "expected"], [
    *zip(BASIC_DOIS, BASIC_DOIS),
    ["10.1109/sp.2011.40"] * 2,
    ["doi10.1177:0146167297234003", "10.1177/0146167297234003"],
    ["10.1177:0146167297234003.pdf", "10.1177/0146167297234003.pdf"],
    ["https://journals.sagepub.com/doi/pdf/10.1177/0146167297234003", "10.1177/0146167297234003"],
    ["https://doi.org/10.1109/sp.2011.40", "10.1109/sp.2011.40"]
])
def test_is_loose_doi_match(suspected, expected):
    print(suspected)
    for ver, regex in enumerate(doi_regexp):
        
        identifiers = re.findall(regex, suspected.lower())
        if identifiers:
            print(f"Matched with {ver} - {identifiers}")
            assert standardise_doi(identifiers[0]) == expected
            return
        print(f"{ver} failed.")
    assert False