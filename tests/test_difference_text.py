# -*- coding: utf-8 -*-

import os
import sys
import pytest

from lxml import etree
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SwiftDiff.text import Text
from SwiftDiff.tokenize import Tokenizer, SwiftSentenceTokenizer
from SwiftDiff.collate import DifferenceText, Collation

class TestDifferenceText:

    @pytest.fixture()
    def base_text(self):
        uri = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/613-07P1.tei.xml')
        base_doc = Tokenizer.parse_text(uri)
        base_text = Text(base_doc, '613-07P1', SwiftSentenceTokenizer)
        return base_text

    @pytest.fixture()
    def variant_text(self):
        uri = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/613-79L2.tei.xml')
        base_doc = Tokenizer.parse_text(uri)
        base_text = Text(base_doc, '613-79L2', SwiftSentenceTokenizer)
        return base_text

    def test_init(self, base_text, variant_text):
        diff_text = DifferenceText(base_text, variant_text, SwiftSentenceTokenizer)

    def test_indents(self, base_text, variant_text):
        diff_text = DifferenceText(base_text, variant_text, SwiftSentenceTokenizer)
        assert diff_text.body.lines[19].value == "|||| Of Xanti's everlasting Tongue,"
        assert diff_text.body.lines[19].other_line.value == " Than lightning's flash, or thunder's roar.Clouds weep, as they do, without pain;"

    def test_line_breaks(self):
        pass
