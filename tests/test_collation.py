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

class TestCollation:

    @pytest.fixture()
    def base_text(self):
        uri = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/613-07P1.tei.xml')
        base_doc = Tokenizer.parse_text(uri)
        base_text = Text(base_doc, '613-07P1', SwiftSentenceTokenizer)
        return base_text

    @pytest.fixture()
    def diff_text(self):
        uri = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/613-07P1.tei.xml')
        base_doc = Tokenizer.parse_text(uri)
        base_text = Text(base_doc, '613-07P1', SwiftSentenceTokenizer)

        uri = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/613-79L2.tei.xml')
        variant_doc = Tokenizer.parse_text(uri)
        variant_text = Text(variant_doc, '613-79L2', SwiftSentenceTokenizer)

        diff_text = DifferenceText(base_text, variant_text, SwiftSentenceTokenizer)

        return diff_text

    def test_init(self, base_text, diff_text):
        diffs = [diff_text]
        tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'xml', '613')

        collation = Collation(base_text, diffs, tei_dir_path)

        assert collation.body[0].witnesses[0]['line'].value == "I OFTEN try'd in vain to find"
        assert collation.body[0].witnesses[0]['line'].base_line.value == "I OFTEN try'd in vain to find"

        assert collation.body[1].witnesses[0]['line'].value == " A Simile for Woman-kind,"
        assert collation.body[1].witnesses[0]['line'].base_line.value == " A simile for woman-kind,"
    def test_indentations(self, base_text, diff_text):
        diffs = [diff_text]
        tei_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'xml', '613')

        collation = Collation(base_text, diffs, tei_dir_path)

        # assert collation.body[19].witnesses[0]['line'].base_line.value == "|||| Of Xanti's everlasting Tongue,"
        # assert collation.body[19].witnesses[0]['line'].base_line.tokens[0].value == "||||"
        assert collation.body[19].witnesses[0]['line'].value == "|||| Of Xanti's everlasting Tongue,"
        assert collation.body[19].witnesses[0]['line'].tokens[0].value == "||||"
