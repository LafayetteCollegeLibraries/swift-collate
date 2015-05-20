import os
import sys
import pytest
import re

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SwiftDiff.tokenizer import ElementToken

class TestElementToken:

    @pytest.fixture
    def tei_stanza(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    def test_init(self, tei_stanza):

        tag = tei_stanza.xpath('local-name()')
        children = list(tei_stanza)

        token = ElementToken(tag, tei_stanza.attrib, children, tei_stanza.text, tei_stanza)
        assert token.name == 'lg'
        assert token.attrib['n'] == '2'

        first_child_tag = token.children[0].xpath('local-name()')
        assert first_child_tag == 'l'

        assert re.search('"Pipe a song about a Lamb!" ', token.text)

        token_b = ElementToken(doc=tei_stanza)
        assert token_b.name == 'lg'
        assert token_b.attrib['n'] == '2'

        first_child_tag = token_b.children[0].xpath('local-name()')
        assert first_child_tag == 'l'

        assert re.search('So I piped with merry chear. ', token.text)

        # Case 3
        nodes = etree.fromstring('<lg n="1"><l xmlns="http://www.tei-c.org/ns/1.0" n="21">(For, <hi rend="underline">Two</hi> of <hi rend="underline">You</hi> make <hi rend="underline">One</hi> of <hi rend="underline">Us</hi>.)</l></lg>')
        node = nodes.xpath('//tei:l', namespaces={'tei': "http://www.tei-c.org/ns/1.0"}).pop()

        token = ElementToken(doc=node)

        assert token.text == '(For, UNDERLINE_CLASS_OPENTwo_CLASS_CLOSED of UNDERLINE_CLASS_OPENYou_CLASS_CLOSED make UNDERLINE_CLASS_OPENOne_CLASS_CLOSED of UNDERLINE_CLASS_OPENUs_CLASS_CLOSED.)'
