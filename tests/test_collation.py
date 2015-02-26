import os
import sys
import pytest

from lxml import etree
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collation import Collation
from tokenizer import Tokenizer

class TestCollation:

    @pytest.fixture
    def diff_tree(self):

        file_paths = map(lambda path: os.path.join(os.path.dirname(os.path.abspath(__file__)), path), ['fixtures/test_tei_a.xml', 'fixtures/test_tei_b.xml'])
        
        tei_stanzas = map(Tokenizer.parse_stanza, file_paths)

        # Work-around
        tei_stanza_u, tei_stanza_v = tei_stanzas[0:2]

        diff_tree = Tokenizer.diff(tei_stanza_u, 'u', tei_stanza_v, 'v')

        return diff_tree

    def test_init(self, diff_tree):

        collation = Collation(diff_tree)

    def test_dict(self, diff_tree):

        collation = Collation(diff_tree)
        collation_dict = collation.to_dict()

        # print collation_dict

        row_a = collation_dict[1]
        base_text_a = row_a[0]

        assert base_text_a['number'] == 1
        assert base_text_a['text'] == 'Piping down the valleys wild, '
        assert base_text_a['distance'] == 0

        assert collation_dict[2][-1]['text'] == 'PIPING SONGS OF PLEASANT GLEE, '
        assert collation_dict[2][-1]['distance'] == 24

    def test_table(self, diff_tree):

        collation = Collation(diff_tree)
        collation_table = collation.table()

        

        pass
