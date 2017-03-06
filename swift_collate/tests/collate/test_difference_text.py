from swift_collate.collate import DifferenceText
from swift_collate.text import Text
from swift_collate.tokenize import SwiftSentenceTokenizer
from lxml import etree
import os
import pytest

@pytest.fixture
def tei_601_14W2():

    file_path = os.path.join('swift_collate', 'tests','fixtures','601-14W2.tei.xml')
    doc = etree.parse(file_path)
    return doc

@pytest.fixture
def tei_601_083Y():

    file_path = os.path.join('swift_collate', 'tests','fixtures','601-083Y.tei.xml')
    doc = etree.parse(file_path)
    return doc

@pytest.fixture
def tei_601_0853():

    file_path = os.path.join('swift_collate','tests','fixtures','601-0853.tei.xml')
    doc = etree.parse(file_path)
    return doc

def test_init():

    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    diff_text = DifferenceText(base_text, [], SwiftSentenceTokenizer)

    assert diff_text.base_text == base_text

def test_merge():

    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    variant_text_083Y = Text(tei_601_083Y(), '601-083Y', SwiftSentenceTokenizer)
    variant_text_0853 = Text(tei_601_0853(), '601-0853', SwiftSentenceTokenizer)

    base_diff_text = DifferenceText(base_text, [], SwiftSentenceTokenizer)
