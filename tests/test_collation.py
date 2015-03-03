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

    def test_values(self, diff_tree):

        collation = Collation(diff_tree)
        collation_values = collation.values()

        print collation_values
        print collation_values.keys()
#        for row,values in collation_values.iteritems():
            
#            print 'trace'
#            print [ line for line in values['line'] if 'line' in values ]

        print collation_values

        row_a = collation_values['lines'][1]
        base_text_a = row_a['line'][0]

        assert base_text_a['number'] == 1
        assert base_text_a['text'] == 'Piping down the valleys wild, '
        assert base_text_a['distance'] == 0

        assert collation_values[2]['line'][-1]['text'] == 'PIPING SONGS OF PLEASANT GLEE, '
        assert collation_values[2]['line'][-1]['distance'] == 24

    def test_str(self, diff_tree):

        collation = Collation(diff_tree)
        assert unicode(collation) == u"""{"1": [{"text": "Piping down the valleys wild, ", "number": 1, "witness": "u", "distance": 0}, {"text": "piping down the valleys wild, ", "number": 1, "witness": "v", "distance": 1}], "2": [{"text": "Piping songs of pleasant glee, ", "number": 2, "witness": "u", "distance": 0}, {"text": "PIPING SONGS OF PLEASANT GLEE, ", "number": 2, "witness": "v", "distance": 24}], "3": [{"text": "On a cloud I saw a child, ", "number": 3, "witness": "u", "distance": 0}, {"text": "On cloud I saw child ", "number": 3, "witness": "v", "distance": 5}], "4": [{"text": "And he laughing said to me: ", "number": 4, "witness": "u", "distance": 0}, {"text": "he laughing said me: ", "number": 4, "witness": "v", "distance": 7}]}"""
        assert str(collation) == """{"1": [{"text": "Piping down the valleys wild, ", "number": 1, "witness": "u", "distance": 0}, {"text": "piping down the valleys wild, ", "number": 1, "witness": "v", "distance": 1}], "2": [{"text": "Piping songs of pleasant glee, ", "number": 2, "witness": "u", "distance": 0}, {"text": "PIPING SONGS OF PLEASANT GLEE, ", "number": 2, "witness": "v", "distance": 24}], "3": [{"text": "On a cloud I saw a child, ", "number": 3, "witness": "u", "distance": 0}, {"text": "On cloud I saw child ", "number": 3, "witness": "v", "distance": 5}], "4": [{"text": "And he laughing said to me: ", "number": 4, "witness": "u", "distance": 0}, {"text": "he laughing said me: ", "number": 4, "witness": "v", "distance": 7}]}"""

    def test_table(self, diff_tree):

        collation = Collation(diff_tree)
        collation_table = collation.table()

        

        pass
