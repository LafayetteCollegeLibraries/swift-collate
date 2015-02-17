import os
import sys
import pytest

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tokenizer import Tokenizer

class TestTokenizer:

    @pytest.fixture
    def tei_xml(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei.xml')) as f:

            data = f.read()

        return data

    @pytest.fixture
    def tei_stanza(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    def test_init(self):

        pass

    def test_parse(self, tei_stanza):

        tokenizer = Tokenizer()
        tree = Tokenizer.parse(tei_stanza)

        assert tree.has_edge('l_@n="1"', 'Piping')
        assert tree.has_edge('l_@n="1"', 'down')
        assert tree.has_edge('l_@n="1"', 'the')
        assert tree.has_edge('l_@n="1"', 'valleys')
        assert tree.has_edge('l_@n="1"', 'wild')

        assert tree.has_edge('l_@n="2"', 'songs')
        assert tree.has_edge('l_@n="3"', 'cloud')
        assert tree.has_edge('l_@n="4"', 'laughing')
