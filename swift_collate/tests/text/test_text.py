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

def test_parse_element():

    doc = tei_601_14W2()
    text = Text(doc, '601-14W2', SwiftSentenceTokenizer)

    line_namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
    title_element = doc.xpath('//tei:title', namespaces=line_namespaces).pop()
    title_result = text.parse_element(title_element)

    headnote_element = doc.xpath('//tei:head[@type="note"]', namespaces=line_namespaces).pop()
    headnote_result = text.parse_element(headnote_element)

    body_element = doc.xpath('//tei:body/tei:div[@type="book"]/tei:div/tei:lg/tei:l[@n]', namespaces=line_namespaces).pop()
    body_result = text.parse_element(body_element)

def test_tokenize():

    text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    
    assert len(text.titles.lines) == 1
    assert len(text.headnotes.lines) == 4
    assert len(text.body.lines) == 220
    assert len(text.footnotes.lines) == 5

    title = text.titles.lines[0]

    assert title.value == "THE BEASTS' CONFESSION TO THE PRIEST,\n        "
