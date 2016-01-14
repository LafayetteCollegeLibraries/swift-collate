# -*- coding: utf-8 -*-

import os
import sys
import pytest

from lxml import etree
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SwiftDiff.text import Text
from SwiftDiff.tokenize import Tokenizer, SwiftSentenceTokenizer

class TestText:

    def test_init(self):
        uri = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/613-07P1.tei.xml')
        base_doc = Tokenizer.parse_text(uri)
        base_text = Text(base_doc, '613-07P1', SwiftSentenceTokenizer)

    def test_indentations(self):
        uri = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/613-07P1.tei.xml')
        base_doc = Tokenizer.parse_text(uri)
        base_text = Text(base_doc, '613-07P1', SwiftSentenceTokenizer)

        assert base_text.body.lines[19].value == "|||| Of Xanti's everlasting Tongue,"
