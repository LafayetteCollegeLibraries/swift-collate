from swift_collate.text import FootnoteLine
from swift_collate.tokenize import SwiftSentenceTokenizer

def test_init():

    line = FootnoteLine('Lorem ipsum dolor sit amet, consectetur adipiscing elit.', 0, '#test-line', 5, SwiftSentenceTokenizer)

    assert line.value == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
    assert line.index == 0
    assert line.tokens == []
    assert line.unaligned_tokens == []
    assert isinstance(line.tokenizer, SwiftSentenceTokenizer)
    assert line.tagger is None
    assert line.classes == {}
    assert line.markup == {}
    assert line.footnotes == []
    assert line.target_id == '#test-line'
    assert line.distance_from_parent == 5
