from swift_collate.text import Token

def test_init():

    token = Token('a', 0)

    assert token.value == 'a'
    assert token.index == 0

def test_normalize_value():

    token = Token('B', 0)
    assert token.normalize_value() == 'b'

    token = Token('.C?', 0)
    assert token.normalize_value() == 'c'
