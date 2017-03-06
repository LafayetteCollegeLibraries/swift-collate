from swift_collate.collate import Collation
from swift_collate.text import Text, TextJSONEncoder
from swift_collate.tokenize import SwiftSentenceTokenizer
from lxml import etree
import os
import pytest
import json

@pytest.fixture
def tei_601_14W2():

    file_path = os.path.join('swift_collate','tests','fixtures','601-14W2.tei.xml')
    doc = etree.parse(file_path)
    return doc

@pytest.fixture
def tei_601_083Y():

    file_path = os.path.join('swift_collate','tests','fixtures','601-083Y.tei.xml')
    doc = etree.parse(file_path)
    return doc

@pytest.fixture
def tei_601_0853():

    file_path = os.path.join('swift_collate','tests','fixtures','601-0853.tei.xml')
    doc = etree.parse(file_path)
    return doc

def test_init():

    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    base_text_data = json.dumps(base_text, cls=TextJSONEncoder)
    base_text_data = json.loads(base_text_data)
    collation = Collation(base_text_data, [], SwiftSentenceTokenizer)
    assert collation.base_text == base_text_data
    assert collation.other_texts == []

    # Test the titles
    assert len(collation.titles) == 1
    first_title = collation.titles[0]
    assert len(first_title['variant_lines']) == 0

    # Test the headnotes
    assert len(collation.headnotes) == 4
    first_headnote = collation.headnotes[0]
    assert len(first_headnote['variant_lines']) == 0

    variant_text = Text(tei_601_083Y(), '601-083Y', SwiftSentenceTokenizer)
    variant_text_data = json.dumps(variant_text, cls=TextJSONEncoder)
    variant_text_data = json.loads(variant_text_data)

    collation_a = Collation(base_text_data, [variant_text_data], SwiftSentenceTokenizer)
    assert collation_a.other_texts == [variant_text_data]
    
    assert len(collation_a.titles[0]['variant_lines']) == 1
    assert len(collation_a.headnotes[0]['variant_lines']) == 1

def test_merge():

    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    base_text.tokenize()
    base_text_data = json.dumps(base_text, cls=TextJSONEncoder)
    base_text_data = json.loads(base_text_data)

    variant_text_a = Text(tei_601_083Y(), '601-083Y', SwiftSentenceTokenizer)
    variant_text_a.tokenize()
    variant_text_a_data = json.dumps(variant_text_a, cls=TextJSONEncoder)
    variant_text_a_data = json.loads(variant_text_a_data)

    collation_a = Collation(base_text_data, [variant_text_a_data], SwiftSentenceTokenizer)

    variant_text_b = Text(tei_601_0853(), '601-0853', SwiftSentenceTokenizer)
    variant_text_b.tokenize()
    variant_text_b_data = json.dumps(variant_text_b, cls=TextJSONEncoder)
    variant_text_b_data = json.loads(variant_text_b_data)

    collation_b = Collation(base_text_data, [variant_text_b_data], SwiftSentenceTokenizer)

    assert collation_a.other_texts == [variant_text_a_data]
    collation_a.merge(collation_b)
    assert collation_a.other_texts == [variant_text_a_data, variant_text_b_data]
