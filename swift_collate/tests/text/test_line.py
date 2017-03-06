from swift_collate.text import Line
from swift_collate.tokenize import SwiftSentenceTokenizer

def test_init():

    line = Line('Lorem ipsum dolor sit amet, consectetur adipiscing elit.', 1, SwiftSentenceTokenizer, None)

    assert line.value == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
    assert line.index == 1
    assert line.tokens == []
    assert line.unaligned_tokens == []
    assert isinstance(line.tokenizer, SwiftSentenceTokenizer)
    assert line.tagger is None
    assert line.classes == {}
    assert line.markup == {}
    assert line.footnotes == []

def test_tokenized():

    line = Line('Quisque ac porta magna, non facilisis dui.', 2, SwiftSentenceTokenizer, None)
    line.tokenize()

    tokens = line.tokens
    assert len(tokens) == 7
    assert map(lambda token: token.value, tokens) == ['Quisque','ac','porta','magna,','non','facilisis','dui.']
