from swift_collate.collate import Collation, CollatedLine
from swift_collate.text import Text, TextJSONEncoder
from swift_collate.tokenize import SwiftSentenceTokenizer
from lxml import etree
import os
import pytest
import json

@pytest.fixture
def tei_601_14W2():

    file_path = os.path.join('tests','fixtures','601-14W2.tei.xml')
    doc = etree.parse(file_path)
    return doc

@pytest.fixture
def tei_601_083Y():

    file_path = os.path.join('tests','fixtures','601-083Y.tei.xml')
    doc = etree.parse(file_path)
    return doc

def test_init():

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

    collated_title = CollatedLine(base_text_title_data, variant_text_title_data)
    assert collated_title.base_line == base_text_title_data
    assert collated_title.line == variant_text_title_data

def test_tokenize():

    base_text = Text(tei_601_14W2(), '601-14W2', SwiftSentenceTokenizer)
    base_text_data = json.dumps(base_text, cls=TextJSONEncoder)
    base_text_data = json.loads(base_text_data)

    base_text_title = base_text_data['titles'].pop()
    base_text_title_data = json.loads(base_text_title)

    variant_text = Text(tei_601_083Y(), '601-083Y', SwiftSentenceTokenizer)
    variant_text_data = json.dumps(variant_text, cls=TextJSONEncoder)
    variant_text_data = json.loads(variant_text_data)

    variant_text_title = variant_text_data['titles'].pop()
    variant_text_title_data = json.loads(variant_text_title)

    collated_title = CollatedLine(base_text_title_data, variant_text_title_data)
    collated_title.tokenize()

    assert len(collated_title.tokens) > 0
    collated_title_data = collated_title.values()
    collated_base_title = collated_title_data['base_line']

    assert len(collated_base_title['tokens']) == 6
    assert map(lambda token: token['value'], collated_base_title['tokens']) == ['THE', "BEASTS'", 'CONFESSION', 'TO', 'THE', 'PRIEST,']

    assert len(collated_title_data['tokens']) == 6
    assert map(lambda token: token['value'], collated_title_data['tokens']) == ['The', 'Beasts', 'Confession', 'to', 'the', 'Priest.']
