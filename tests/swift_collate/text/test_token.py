from swift_collate.text import Token

def test_init():

    token = Token('a', 0)

    assert token.value == 'a'
    assert token.index == 0
