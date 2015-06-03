import os
import sys
import pytest

from lxml import etree
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tokenizer import Tokenizer, ElementToken

class TestTokenizer:

    @pytest.fixture
    def tei_xml(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei.xml')) as f:

            data = f.read()

        return data

    @pytest.fixture
    def tei_doc(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems[0]

        return elem

    @pytest.fixture
    def tei_doc_a(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_a.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_doc_b(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_b.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_doc_c(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_c.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_doc_d(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_d.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_doc_e(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_e.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_doc_f(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_f.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_swift_R56503P1(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_swift_36629.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    @pytest.fixture
    def tei_swift_R56503P3(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_swift_36711.tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

        return elem

    def test_init(self):

        pass

    def test_parse(self, tei_doc, tei_swift_R56503P1, tei_swift_R56503P3):

        tokenizer = Tokenizer()
        tree = Tokenizer.parse(tei_doc)

#        assert tree.has_edge('<lg n="1"/l n="1" />', 'Piping down the valleys wild, ')

#        assert tree.has_edge('<lg n="1"/l n="2" />', 'Piping songs of pleasant glee, ')
#        assert tree.has_edge('<lg n="1"/l n="3" />', 'On a cloud I saw a child, ')
#        assert tree.has_edge('<lg n="1"/l n="4" />', 'And he laughing said to me: ')

        # Test for structural alignment
        tree_2 = Tokenizer.parse(tei_doc)

    def test_stanza_diff(self, tei_doc_a, tei_doc_b):

        tokenizer = Tokenizer()

        diff_tree = Tokenizer.diff(tei_doc_a, 'a', tei_doc_b, 'b')

#        assert diff_tree['<l n="3" />']['On a cloud I saw a child, ']['distance'] == nltk.metrics.distance.edit_distance('On a cloud I saw a child, ', 'On cloud I saw child ')

    def test_struct_diff(self, tei_doc_a, tei_doc_c):

        tokenizer = Tokenizer()
        
        diff_tree = Tokenizer.diff(tei_doc_a, 'a', tei_doc_c, 'c')
        
#        assert diff_tree['<l n="3" />']['On a cloud I saw a child, ']['distance'] == nltk.metrics.distance.edit_distance('On a cloud I saw a child, ', 'On a cloud I  saw  a child, ')
#        assert diff_tree['<l n="4" />']['And he laughing said to me: ']['distance'] == nltk.metrics.distance.edit_distance('And he laughing said to me: ', 'And he laughing said to me: ')

    def test_text_diff(self, tei_doc_a, tei_doc_b, tei_doc_c):

        tokenizer = Tokenizer()

        diff_tree = Tokenizer.diff(tei_doc_a, 'a', tei_doc_c, 'c')

    def test_stemma(self, tei_doc_a, tei_doc_b, tei_doc_c):

        tokenizer = Tokenizer()

        base_text = { 'node': tei_doc_a, 'id': 'a' }
        witnesses = [ { 'node': tei_doc_b, 'id': 'b' }, { 'node': tei_doc_c, 'id': 'c' } ]

        stemma = Tokenizer.stemma(base_text, witnesses)

    def test_stemma_alignment(self, tei_doc_d, tei_doc_e, tei_doc_f):

        base_text = { 'node': tei_doc_d, 'id': 'd' }
        witnesses = [ { 'node': tei_doc_e, 'id': 'e' }, { 'node': tei_doc_f, 'id': 'f' } ]

        stemma = Tokenizer.stemma(base_text, witnesses)

    def test_parse_stanza(self):

        tei_stanza = Tokenizer.parse_stanza(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei.xml'))

        lg_elems = tei_stanza.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        assert len(lg_elems) > 0

        lg_elem = lg_elems.pop()

        assert lg_elem.xpath('local-name()') == 'lg'

    def test_parse_text(self):

        tei_text = Tokenizer.parse_text(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei.xml'))

        lg_elems = tei_text.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        assert len(lg_elems) == 2

        lg_elem = lg_elems.pop()

        assert lg_elem.xpath('local-name()') == 'lg'
        assert tei_text.xpath('local-name()') == 'text'

    def test_clean_tokens(self):

        tokens4 = ['"', "text"]
        tokens4 = Tokenizer.clean_tokens(tokens4)

#        assert tokens4 == ['"text']

        tokens1 = ['Gen', "'ral"]
        tokens1 = Tokenizer.clean_tokens(tokens1)

#        assert tokens1 == ["Gen'ral"]

        tokens2 = ['test', 'Gen', "'ral"]
        tokens2 = Tokenizer.clean_tokens(tokens2)

#        assert tokens2 == ['test', "Gen'ral"]

        tokens3 = ['Gen', "'ral", 'test']
        tokens3 = Tokenizer.clean_tokens(tokens3)

#        assert tokens3 == ["Gen'ral", 'test']

        tokens4 = ['In', 'Fable', 'all', 'things', 'hold', 'Discourse']
        tokens4 = Tokenizer.clean_tokens(tokens4)

        tokens5 = ['DISPLAY-INITIAL_CLASS_OPENIDISPLAY-INITIAL_CLASS_CLOSEDN', 'Fable', 'all', 'things', 'hold', 'Discourse', ';', 'Then', 'UNDERLINE_CLASS_OPENWordsUNDERLINE_CLASS_CLOSED', ',', 'no', 'doubt', ',', 'must', 'talk', 'of', 'course.']
        tokens5 = Tokenizer.clean_tokens(tokens5)

#        assert tokens5 == ['DISPLAY-INITIAL_CLASS_OPENIDISPLAY-INITIAL_CLASS_CLOSEDN', 'Fable', 'all', 'things', 'hold', 'Discourse', ';', 'Then', 'UNDERLINE_CLASS_OPENWordsUNDERLINE_CLASS_CLOSED', ',', 'no', 'doubt', ',', 'must', 'talk', 'of', 'course.']

    def test_element_token(self):
        
        nodes = etree.fromstring('<lg n="1"><l xmlns="http://www.tei-c.org/ns/1.0" n="21">(For, <hi rend="underline">Two</hi> of <hi rend="underline">You</hi> make <hi rend="underline">One</hi> of <hi rend="underline">Us</hi>.)</l></lg>')
        node = nodes.xpath('//tei:l', namespaces={'tei': "http://www.tei-c.org/ns/1.0"}).pop()

        token = ElementToken(doc=node)
        assert token.text == '(For, _CLASS_OPENTwo_CLASS_CLOSED of _CLASS_OPENYou_CLASS_CLOSED make _CLASS_OPENOne_CLASS_CLOSED of _CLASS_OPENUs_CLASS_CLOSED.)'

