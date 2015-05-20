# -*- coding: utf-8 -*-

import os
import sys
import pytest

from lxml import etree
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from collation import Collation
from SwiftDiff.collation import Collation

# from tokenizer import Tokenizer
from SwiftDiff.tokenizer import Tokenizer

class TestCollation:

    @pytest.fixture()
    def diff_tree(self, request):

        file_paths = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['fixtures/test_tei_a.xml', 'fixtures/test_tei_b.xml'])
        
        # tei_stanzas = map(Tokenizer.parse_stanza, file_paths)
        tei_stanzas = map(Tokenizer.parse_text, file_paths)

        # Work-around
        tei_stanza_u, tei_stanza_v = tei_stanzas[0:2]

        diff_tree = Tokenizer.diff(tei_stanza_u, 'u', tei_stanza_v, 'v')

        return diff_tree

    @pytest.fixture()
    def diff_tree_tags(self, request):

        file_paths = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['fixtures/test_tei_a.xml', 'fixtures/test_tei_c.xml'])
        
        tei_stanzas = map(Tokenizer.parse_stanza, file_paths)

        # Work-around
        tei_stanza_u, tei_stanza_v = tei_stanzas[0:2]

        diff_tree = Tokenizer.diff(tei_stanza_u, 'u', tei_stanza_v, 'v')

        return diff_tree

    @pytest.fixture()
    def stemma(self, request):

        file_paths = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['fixtures/test_tei_a.xml', 'fixtures/test_tei_b.xml', 'fixtures/test_tei_c.xml'])

        tei_stanzas = map(Tokenizer.parse_text, file_paths)

        base_text = tei_stanzas.pop()

        witnesses = [ { 'node': tei_stanzas[0], 'id': 'v' }, { 'node': tei_stanzas[1], 'id': 'w' } ]

        diff_tree = Tokenizer.stemma({ 'node': base_text, 'id': 'u' }, witnesses)

        return diff_tree

    @pytest.fixture()
    def stemma_alignment(self, request):

        file_paths = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['fixtures/test_tei_d.xml', 'fixtures/test_tei_e.xml', 'fixtures/test_tei_f.xml'])

        tei_stanzas = map(Tokenizer.parse_text, file_paths)

        base_text = tei_stanzas.pop()

        witnesses = [ { 'node': tei_stanzas[0], 'id': 'v' }, { 'node': tei_stanzas[1], 'id': 'w' } ]

        diff_tree = Tokenizer.stemma({ 'node': base_text, 'id': 'u' }, witnesses)

        return diff_tree

    @pytest.fixture()
    def stemma_alignment_b(self):

        file_paths = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['fixtures/test_swift_36629.xml', 'fixtures/test_swift_36711.tei.xml'])
        tei_stanzas = map(Tokenizer.parse_text, file_paths)

        base_text = tei_stanzas.pop()

        witnesses = [ { 'node': tei_stanzas[0], 'id': 'v' } ]

        diff_tree = Tokenizer.stemma({ 'node': base_text, 'id': 'u' }, witnesses)

        return diff_tree

    @pytest.fixture()
    def stemma_R565(self):

        file_paths = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['fixtures/test_swift_36629.xml',
                                                                                                       'fixtures/test_swift_36670.xml'])
        tei_stanzas = map(Tokenizer.parse_text, file_paths)

        base_text = tei_stanzas[0]
        witnesses = [ { 'node': tei_stanzas[-1], 'id': "R56503P2" } ]

        stemma_R565 = Tokenizer.stemma({ 'node': base_text, 'id': 'base' }, witnesses)
        return stemma_R565

    def test_init(self, diff_tree, stemma, stemma_R565):

        # Base case
        collation = Collation(diff_tree)
        collation_values = collation.values()

        row_a = collation_values['lines'][5]
        base_text_a = row_a['line'][0]

        assert base_text_a['number'] == 5

        # Case 1
        collation_R565 = Collation(stemma_R565)
        collation_R565_values = collation_R565.values()

        collation_R565_lines = collation_R565_values['lines']

        # Line 1
        collation_R565_line_1 = collation_R565_lines[1]

        collation_R565_line_1_ngrams_sorted = collation_R565_line_1['ngrams_sorted']

        # ngrams within Line 1
        base_ngrams = collation_R565_line_1_ngrams_sorted[0]

        assert 'DISPLAY-INITIAL_CLASS_OPENIDISPLAY-INITIAL_CLASS_CLOSEDN' in base_ngrams['line_ngrams']
        assert 'Discourse;' in base_ngrams['line_ngrams']

        R56503P2_ngrams = collation_R565_line_1_ngrams_sorted[1]

        assert 'DISPLAY-INITIAL_CLASS_OPENIDISPLAY-INITIAL_CLASS_CLOSEDN' in R56503P2_ngrams['line_ngrams']
        assert 'Discourse;' in R56503P2_ngrams['line_ngrams']

        # Line 3
        collation_R565_line_3 = collation_R565_lines[3]

        assert 'ngrams_sorted' in collation_R565_line_3

        collation_R565_line_3_ngrams_sorted = collation_R565_line_3['ngrams_sorted']

        # ngrams within Line 3
        base_ngrams = collation_R565_line_3_ngrams_sorted[0]

        # Once on a Time, near <hi rend="underline">Channel-Row
        assert 'INDENT_ELEMENTOnce' in base_ngrams['line_ngrams']
        assert 'UNDERLINE_CLASS_OPENChannel-RowUNDERLINE_CLASS_CLOSED,' in base_ngrams['line_ngrams']

        # Once on a Time, near <hi rend="underline">Channel-Row</hi>
        R56503P2_ngrams = collation_R565_line_3_ngrams_sorted[1]

        assert 'INDENT_ELEMENTOnce' in R56503P2_ngrams['line_ngrams']
        assert 'UNDERLINE_CLASS_OPENChannel-RowUNDERLINE_CLASS_CLOSED,' in R56503P2_ngrams['line_ngrams']

    def test_values_stemma(self, stemma):

        collation = Collation(stemma)
        collation_values = collation.values()

        lines = collation_values['lines']

        line_1 = lines[1]

    

    def test_stemma_alignment(self, stemma_alignment, stemma_alignment_b):

        collation = Collation(stemma_alignment)
        collation_values = collation.values()

        lines = collation_values['lines']

        # One extraneous token
        line_1 = lines[1]
        assert line_1['ngram']['u'] == ['Piping', 'down', 'the', 'valleys', 'wild,']

        # Two additional tokens
        line_3 = lines[3]
        assert line_3['ngram']['u'] == ['On', 'a', 'cloud', 'I', 'saw', 'a', 'child,']
        # assert line_3['line'][2]['text'] == 'On Lorem a cloud I saw a amet child, '

        # One token at a distance of 2 steps
        line_4 = lines[4]
        assert line_4['ngram']['u'] == ['And', 'he', 'laughing', 'said', 'to', 'me:']

        #
        #

        collation_b = Collation(stemma_alignment_b)
        collation_values_b = collation_b.values()

        lines_b = collation_values_b['lines']

    def test_values(self, diff_tree, diff_tree_tags):

        collation = Collation(diff_tree)
        collation_values = collation.values()

        row_a = collation_values['lines'][5]
        base_text_a = row_a['line'][0]

        assert base_text_a['number'] == 5

#        row_a = collation_values['lines'][1]
#        base_text_a = row_a['line'][0]
#
#        assert base_text_a['number'] == 1
#        assert base_text_a['text'] == 'Piping down the valleys wild, '
#        assert base_text_a['distance'] == 0
#
#        row_b = collation_values['lines'][2]
#        base_text_b = row_b['line'][-1]
#
#        assert base_text_b['text'] == 'PIPING SONGS OF PLEASANT GLEE, '
#        assert base_text_b['distance'] == 24
#
#        # Testing for collations involving TEI tags
#        collation = Collation(diff_tree_tags)
#        collation_values = collation.values()
#
#        row_a = collation_values['lines'][1]
#        base_text_a = row_a['line'][0]
#
#        assert base_text_a['number'] == 1
#        assert base_text_a['text'] == 'Piping down the valleys wild, '
#        assert base_text_a['distance'] == 0
#
#        row_b = collation_values['lines'][2]
#        base_text_b = row_b['line'][-1]
#
#        assert base_text_b['text'] == u'Piping «gap» songs of pleasant glee, '
#        assert base_text_b['distance'] == 6
#
#        # Analyze the line ngram tokens
#        row_b_ngrams = row_b['ngram']
#
#        assert row_b_ngrams['base'] == ['Piping', '', '', '', '', '']
#        assert row_b_ngrams['v'] == ['', u'«gap»', 'songs', 'of', 'pleasant', 'glee']
#        assert row_b_ngrams['u'] == ['', 'songs', 'of', 'pleasant', 'glee', ',']
