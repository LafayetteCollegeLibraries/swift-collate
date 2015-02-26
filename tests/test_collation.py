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

        diff_tree = Tokenizer.diff(tei_stanza_u, tei_stanza_v)

        return diff_tree

    def test_init(self, diff_tree):

        collation = Collation(diff_tree)

    def test_list(self, diff_tree):

        collation = Collation(diff_tree)
        collation_list = collation.__list__()

        assert collation_list[0][0] == 1
        assert collation_list[0][1] == 'Piping down the valleys wild, '

        assert collation_list[1][1] == 'Piping songs of pleasant glee, '
        assert collation_list[1][2] == 24

    def test_table(self, diff_tree):

        collation = Collation(diff_tree)
        collation_table = collation.table()

        

        pass
