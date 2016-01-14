# -*- coding: utf-8 -*-

import os
import sys
import pytest

from lxml import etree
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SwiftDiff.text import Line
from SwiftDiff.tokenize import SwiftSentenceTokenizer

class TestLine:

    def test_init(self):
        base_line = Line("Lorem ipsum dolor sit", 0, SwiftSentenceTokenizer)
        base_line.tokenize()

        assert base_line.tokens[0].value == 'Lorem'
        assert base_line.tokens[1].value == 'ipsum'
        assert base_line.tokens[2].value == 'dolor'
        assert base_line.tokens[3].value == 'sit'
