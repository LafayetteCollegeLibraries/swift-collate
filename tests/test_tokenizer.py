import os
import sys
import pytest

from lxml import etree
import nltk

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

    @pytest.fixture
    def tei_stanza_a(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_a.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_stanza_b(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_b.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_stanza_c(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_c.xml')) as f:

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

        assert tree.has_edge('<l n="1" />', 'Piping down the valleys wild, ')

        assert tree.has_edge('<l n="2" />', 'Piping songs of pleasant glee, ')
        assert tree.has_edge('<l n="3" />', 'On a cloud I saw a child, ')
        assert tree.has_edge('<l n="4" />', 'And he laughing said to me: ')

    def test_text_diff(self, tei_stanza_a, tei_stanza_b):

        tokenizer = Tokenizer()

        diff_tree = Tokenizer.diff(tei_stanza_a, tei_stanza_b)
        
        assert diff_tree['<l n="3" />']['On a cloud I saw a child, ']['distance'] == nltk.metrics.distance.edit_distance('On a cloud I saw a child, ', 'On cloud I saw child ')

    def test_struct_diff(self, tei_stanza_a, tei_stanza_c):

        tokenizer = Tokenizer()
        
        diff_tree = Tokenizer.diff(tei_stanza_a, tei_stanza_c)

        assert diff_tree['<l n="3" />']['On a cloud I saw a child, ']['distance'] == nltk.metrics.distance.edit_distance('On a cloud I saw a child, ', 'On a cloud I  saw  a child, ')
