from swift_collate.collate import Collation, CollatedLine, CollatedToken
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

    variant_text = Text(tei_601_083Y(), '601-083Y', SwiftSentenceTokenizer)
    variant_text_data = json.dumps(variant_text, cls=TextJSONEncoder)
    variant_text_data = json.loads(variant_text_data)

    variant_text_title = variant_text_data['titles'].pop()
    variant_text_title_data = json.loads(variant_text_title)

    collated_title = CollatedLine(base_text_title_data, variant_text_title_data)
    collated_title.tokenize()

    collated_title_data = collated_title.values()
    collated_base_title = collated_title_data['base_line']

    base_token_data = collated_base_title['tokens'][0]
    variant_token_data = collated_base_title['tokens'][0]

    token = CollatedToken(base_token_data, variant_token_data)
    assert token.base_token == base_token_data
    assert token.token == variant_token_data
