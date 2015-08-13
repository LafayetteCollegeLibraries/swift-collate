import os
import sys
import pytest

from lxml import etree
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SwiftDiff.tokenizer import Tokenizer, ElementToken

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

            # Append the <title> elements for the purposes of analysis
            title_elems = doc.xpath('//tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem.extend(title_elems)

        return elem

    @pytest.fixture
    def tei_doc_c(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_c.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

            # Append the <title> elements for the purposes of analysis
            title_elems = doc.xpath('//tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem.extend(title_elems)

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
    def tei_doc_g(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_tei_g.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

            # Append the <title> elements for the purposes of analysis
            title_elems = doc.xpath('//tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem.extend(title_elems)

        return elem

    @pytest.fixture
    def tei_doc_R56503P1(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_swift_36629.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
        return doc

    @pytest.fixture
    def tei_doc_R56503P2(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_swift_36670.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
        return doc

    @pytest.fixture
    def tei_doc_R56503P3(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/test_swift_36711.tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
        return doc

    @pytest.fixture
    def swift_250_0202(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/swift_250_0202.tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
        return doc
        pass

    @pytest.fixture
    def swift_250_03P1(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/swift_250_03P1.tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
        return doc
        pass

    @pytest.fixture
    def swift_250_422R(self):

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/swift_250_422R.tei.xml')) as f:

            data = f.read()
            doc = etree.fromstring(data)
        return doc
        pass

    def test_init(self):

        pass

    # Tokenizer.text_tree()
    #
    # Verifies the structure of the graph modeling the tree of structure of the TEI-XML Document
    def test_text_tree(self, tei_doc_R56503P1, tei_doc_R56503P2, tei_doc_R56503P3):

        # Case 1
        tree = Tokenizer.text_tree(tei_doc_R56503P1)

        assert '<lg n="1"/l n="3" />' in tree
        assert '<lg n="2"/l n="3" />' in tree

        tree = Tokenizer.text_tree(tei_doc_R56503P2)

        assert '<lg n="1"/l n="3" />' in tree

        # Case 2
        tree = Tokenizer.text_tree(tei_doc_R56503P3)

        assert '<lg n="1"/l n="3" />' in tree
        assert '<lg n="2"/l n="3" />' in tree

        # edges = tree['<lg n="2"/l n="3" />'].items()

        # edge = edges[0]
        # line_text = edge[0]
        
        # assert line_text == 'INDENT_ELEMENTOSMALL-CAPS_CLASS_OPENNCESMALL-CAPS_CLASS_CLOSED on a Time, near UNDERLINE_CLASS_OPENChannel-RowUNDERLINE_CLASS_CLOSED,'

    def test_text_tree_footnotes(self, tei_doc_g, tei_doc_c):

        tree = Tokenizer.text_tree(tei_doc_g, 'g')
        assert '<l n="1-footnotes" />' in tree

        tree = Tokenizer.text_tree(tei_doc_c, 'c')
        assert '<l n="1-footnotes" />' in tree

    def test_text_tree_headnotes(self, tei_doc_g, tei_doc_b, tei_doc_c):

        tree = Tokenizer.text_tree(tei_doc_g, 'g')
        assert '<l n="1-headnotes" />' in tree

        tree = Tokenizer.text_tree(tei_doc_b, 'b')
        assert '<l n="1-headnotes" />' in tree

    def test_text_tree_titles(self, tei_doc_g, tei_doc_b, tei_doc_c):

        tree = Tokenizer.text_tree(tei_doc_g, 'g')
        assert '<l n="1-titles" />' in tree

        tree = Tokenizer.text_tree(tei_doc_b, 'b')
        assert '<l n="1-titles" />' in tree

    # Tokenizer.text_tree()
    #
    def test_parse(self, tei_doc, tei_doc_R56503P2, tei_doc_R56503P3):

        tree = Tokenizer.parse(tei_doc)

        elems = tei_doc_R56503P3.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        tree_2 = Tokenizer.parse(elems[3])

        line_2_text = tree_2['<l n="2" />'].keys()[0]

        assert line_2_text == 'Then UNDERLINE_CLASS_OPENWordsUNDERLINE_CLASS_CLOSED, no doubt, must talk of Course.'

        tree_3b = Tokenizer.parse(elems[4])
        line_3_text = tree_3b['<l n="3" />'].keys()[0]
        
        assert line_3_text == 'INDENT_ELEMENTOSMALL-CAPS_CLASS_OPENNCESMALL-CAPS_CLASS_CLOSED on a Time, near UNDERLINE_CLASS_OPENChannel-RowUNDERLINE_CLASS_CLOSED,'

    # Tokenizer.diff()
    #
    # Verifies the structure of the graph modeling a stemmatic tree capturing the textual differences between two (and only two) TEI Documents
    def test_diff(self, tei_doc_a, tei_doc_c, tei_doc_R56503P1, tei_doc_R56503P2):

        tokenizer = Tokenizer()

        diff_tree = Tokenizer.diff(tei_doc_a, 'a', tei_doc_c, 'c')

        assert diff_tree is not None

        diff_tree = Tokenizer.diff(tei_doc_R56503P1, 'R56503P1',
                                   tei_doc_R56503P2, 'R56503P2')

        assert '<l n="3" />' in diff_tree

        keys = filter(lambda text_token: text_token.value == 'near', diff_tree['<l n="3" />'].keys())
        key = keys.pop()

        values = diff_tree['<l n="3" />'][key]
        assert 'distance' in values
        assert values['distance'] == 0

        assert 'feature' in values
        assert values['feature'] == 'ngram'

        assert 'witness' in values
        assert values['witness'] != 'base'

        assert 'position' in values
        assert values['position'] == 4

    def test_stanza_diff(self, tei_doc_a, tei_doc_b):

        tokenizer = Tokenizer()

        diff_tree = Tokenizer.diff(tei_doc_a, 'a', tei_doc_b, 'b')

        # assert diff_tree['<l n="3" />']['On a cloud I saw a child, ']['distance'] == nltk.metrics.distance.edit_distance('On a cloud I saw a child, ', 'On cloud I saw child ')

    def test_struct_diff(self, tei_doc_a, tei_doc_c):

        tokenizer = Tokenizer()
        
        diff_tree = Tokenizer.diff(tei_doc_a, 'a', tei_doc_c, 'c')
        
#        assert diff_tree['<l n="3" />']['On a cloud I saw a child, ']['distance'] == nltk.metrics.distance.edit_distance('On a cloud I saw a child, ', 'On a cloud I  saw  a child, ')
#        assert diff_tree['<l n="4" />']['And he laughing said to me: ']['distance'] == nltk.metrics.distance.edit_distance('And he laughing said to me: ', 'And he laughing said to me: ')

    # Tokenizer.stemma()
    #
    # Verifies the structure of the graph modeling a stemmatic tree capturing the textual differences between two or more TEI Documents
    def test_stemma(self, tei_doc_a, tei_doc_b, tei_doc_c, tei_doc_R56503P1, tei_doc_R56503P2, tei_doc_R56503P3):

        tokenizer = Tokenizer()

        base_text = { 'node': tei_doc_a, 'id': 'a' }
        witnesses = [ { 'node': tei_doc_b, 'id': 'b' }, { 'node': tei_doc_c, 'id': 'c' } ]

        # stemma = Tokenizer.stemma(base_text, witnesses)

        ####
        base_text = { 'node': tei_doc_R56503P1, 'id': 'base' }
        witnesses = [ { 'node': tei_doc_R56503P2, 'id': "R56503P2" }, { 'node': tei_doc_R56503P3, 'id': "R56503P3" } ]
        stemma = Tokenizer.stemma(base_text, witnesses)

        assert '<l n="3" />' in stemma

        keys = filter(lambda text_token: text_token.value == 'Time,', stemma['<l n="3" />'].keys())
        keys = filter(lambda key: stemma['<l n="3" />'][key]['feature'] == 'ngram', keys)

        assert len(keys) == 3

        assert 'witness' in stemma['<l n="3" />'][keys[0]]

        features = filter(lambda key: stemma['<l n="3" />'][key]['witness'] == 'R56503P2', keys)
        assert len(features) == 1
        
        key = features.pop()
            
        values = stemma['<l n="3" />'][key]

        assert 'distance' in values
        assert values['distance'] == 0

        assert 'feature' in values
        assert values['feature'] == 'ngram'

        assert values['witness'] != 'base'

        assert 'position' in values
        assert values['position'] == 3

    def test_stemma_footnotes(self, tei_doc_g, tei_doc_b, tei_doc_c):

        base_text = { 'node': tei_doc_c, 'id': 'base' }
        witnesses = [ { 'node': tei_doc_g, 'id': "a" }, { 'node': tei_doc_b, 'id': "b" } ]
        stemma = Tokenizer.stemma(base_text, witnesses)

        assert '<lg n="1-footnotes"/l n="1" />' in stemma

        text_nodes = stemma['<lg n="1-footnotes"/l n="1" />'].keys()
        text_node_values = map(lambda text_node: text_node.value, text_nodes)

        assert 'Lorem ipsum' in text_node_values
        assert 'Lorem' in text_node_values
        assert 'ipsum' in text_node_values

        assert 'dolor sit amet' in text_node_values
        assert 'dolor' in text_node_values
        assert 'sit' in text_node_values

        # "amet" is ommitted due to the alignment process
        # assert 'amet' in text_node_values

    def test_stemma_headnotes(self, tei_doc_g, tei_doc_b, tei_doc_c):

        base_text = { 'node': tei_doc_c, 'id': 'base' }
        witnesses = [ { 'node': tei_doc_g, 'id': "a" }, { 'node': tei_doc_b, 'id': "b" } ]
        stemma = Tokenizer.stemma(base_text, witnesses)

        assert '<lg n="1-headnotes"/l n="1" />' in stemma

        text_nodes = stemma['<lg n="1-headnotes"/l n="1" />'].keys()
        text_node_values = map(lambda text_node: text_node.value, text_nodes)

        assert 'Songs of Innocence' in text_node_values
        assert 'Songs' in text_node_values
        assert 'of' in text_node_values
        assert 'Innocence' in text_node_values

#        assert 'Songs of Guilt' in text_node_values
#        assert 'Guilt' in text_node_values

        assert 'My Innocent Songs' in text_node_values
        assert 'My' in text_node_values
        assert 'Innocent' in text_node_values

    def test_stemma_titles(self, tei_doc_g, tei_doc_b, tei_doc_c):

        base_text = { 'node': tei_doc_c, 'id': 'base' }
        witnesses = [ { 'node': tei_doc_g, 'id': "a" }, { 'node': tei_doc_b, 'id': "b" } ]
        stemma = Tokenizer.stemma(base_text, witnesses)

        assert '<lg n="1-titles"/l n="1" />' in stemma

    def test_stanza_diff_titles(self, tei_doc_g, tei_doc_b, tei_doc_c,
                                tei_doc_R56503P1, tei_doc_R56503P2, tei_doc_R56503P3):

        tokenizer = Tokenizer()

#        diff_tree = Tokenizer.diff(tei_doc_g, 'g', tei_doc_b, 'b')
        diff_tree = Tokenizer.diff(tei_doc_R56503P1, 'R56503P1', tei_doc_R56503P2, 'R56503P2')
#        diff_tree = Tokenizer.diff(tei_doc_R56503P2, 'R56503P2', tei_doc_R56503P3, 'R56503P3')

        assert '<lg n="1-titles"/l n="1" />' in diff_tree

#        text_node = filter( lambda text_node: text_node.value == '', diff_tree.edges() )

#        print( text_node[0] )
#        print( map(lambda text_node: text_node.value, diff_tree['<lg n="1-titles"/l n="1" />'].keys()) )

        for text_node, values in diff_tree['<lg n="1-titles"/l n="1" />'].items():

            print(text_node.value)
            print(values)

        pass

    def test_stanza_stemma_titles(self, tei_doc_g, tei_doc_b, tei_doc_c,
                                  tei_doc_R56503P1, tei_doc_R56503P2, tei_doc_R56503P3):

        tokenizer = Tokenizer()

        diff_tree = Tokenizer.stemma( {'node': tei_doc_R56503P1, 'id': 'R56503P1'},
                                      [ {'node': tei_doc_R56503P2, 'id': 'R56503P2'},
                                        {'node': tei_doc_R56503P3, 'id': 'R56503P3'} ])

        assert '<lg n="1-titles"/l n="1" />' in diff_tree

        for text_node, values in diff_tree['<lg n="1-titles"/l n="1" />'].items():

            print(text_node.value)
            print(values)

        assert False

        
        pass


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
        
