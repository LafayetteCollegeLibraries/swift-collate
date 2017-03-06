from swift_collate.collate import Collation, CollatedLines
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

def test_init():

    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    base_text_data = json.dumps(base_text, cls=TextJSONEncoder)
    base_text_data = json.loads(base_text_data)
    collation = Collation(base_text_data, [], SwiftSentenceTokenizer)

    base_text_title = base_text_data['titles'].pop()
    base_text_title_data = json.loads(base_text_title)

    collated_titles = CollatedLines(base_text_title_data)
    assert collated_titles.base_line == base_text_title_data

def test_add_variant_line():
    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    base_text_data = json.dumps(base_text, cls=TextJSONEncoder)
    base_text_data = json.loads(base_text_data)
    collation = Collation(base_text_data, [], SwiftSentenceTokenizer)

    base_text_title = base_text_data['titles'].pop()
    base_text_title_data = json.loads(base_text_title)

    variant_text = Text(tei_601_083Y(), '601-083Y', SwiftSentenceTokenizer)
    variant_text_data = json.dumps(variant_text, cls=TextJSONEncoder)
    variant_text_data = json.loads(variant_text_data)

    variant_text_title = variant_text_data['titles'].pop()
    variant_text_title_data = json.loads(variant_text_title)

    collated_titles = CollatedLines(base_text_title_data)
    collated_base_line_data = collated_titles.values()
    assert collated_base_line_data['base_line'] == base_text_title_data
    assert collated_titles.variant_lines == []

    collated_titles.add_variant_line(variant_text_title_data)
    assert len(collated_titles.variant_lines) > 0
    variant_line = collated_titles.variant_lines[0]

def test_align():
    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    base_text_data = json.dumps(base_text, cls=TextJSONEncoder)
    base_text_data = json.loads(base_text_data)
    collation = Collation(base_text_data, [], SwiftSentenceTokenizer)

    base_text_title = base_text_data['titles'].pop()
    base_text_title_data = json.loads(base_text_title)

    variant_text = Text(tei_601_083Y(), '601-083Y', SwiftSentenceTokenizer)
    variant_text_data = json.dumps(variant_text, cls=TextJSONEncoder)
    variant_text_data = json.loads(variant_text_data)

    variant_text_title = variant_text_data['titles'].pop()
    variant_text_title_data = json.loads(variant_text_title)

    collated_titles = CollatedLines(base_text_title_data)
    collated_base_line_data = collated_titles.values()

    # Trivial case
    collated_titles.add_variant_line(variant_text_title_data)
    collated_titles.align()
    assert len(collated_titles.base_line['tokens']) == len(collated_titles.variant_lines[0].tokens)
    
    # Cases where the length of a line in the variant exceeds that of the base
    variant_text_title_data = json.loads(variant_text_title)
    variant_line_length = len(variant_text_title_data)

    variant_text_title_data['tokens'].append({u'index': 6, u'distance': 0, u'markup': {}, u'value': u'some', u'classes': [], u'normal_value': u'some'})
    variant_text_title_data['tokens'].append({u'index': 7, u'distance': 0, u'markup': {}, u'value': u'extra', u'classes': [], u'normal_value': u'extra'})
    variant_text_title_data['tokens'].append({u'index': 8, u'distance': 0, u'markup': {}, u'value': u'words', u'classes': [], u'normal_value': u'words'})

    collated_titles.add_variant_line(variant_text_title_data)
    variant_line = collated_titles.variant_lines[0]
    base_title_length = len(base_text_title_data['tokens'])
    collated_titles.align()

    assert len(collated_titles.base_line['tokens']) == base_title_length + 3

    # Cases where the length of a line in the base...
    variant_text_title_data = json.loads(variant_text_title)
    variant_line_length = len(variant_text_title_data)

    base_text_title_data['tokens'].append({u'index': 6, u'distance': 0, u'markup': {}, u'value': u'some', u'classes': [], u'normal_value': u'some'})
    base_text_title_data['tokens'].append({u'index': 7, u'distance': 0, u'markup': {}, u'value': u'extra', u'classes': [], u'normal_value': u'extra'})
    base_text_title_data['tokens'].append({u'index': 8, u'distance': 0, u'markup': {}, u'value': u'words', u'classes': [], u'normal_value': u'words'})
    
    collated_titles = CollatedLines(base_text_title_data)
    collated_titles.add_variant_line(variant_text_title_data)
    variant_line = collated_titles.variant_lines[0]
    collated_titles.align()

    assert len(collated_titles.variant_lines[0].tokens) == variant_line_length + 3
