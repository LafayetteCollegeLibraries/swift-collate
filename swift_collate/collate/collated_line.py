import json
from nltk.metrics import distance as nltk_distance
from collated_token import CollatedToken
from ..text import Token
from ..text.token import TokenJSONEncoder

class CollatedLine(object):

    def __init__(self, base_line, line):

        self.base_line = base_line
        self.line = line
        self.tokens = []
#        self.unaligned_tokens = []
#        self.distance = self.find_distance(base_line, line)
#        self.position = ''
        self.index = line['index']

    def tokenize(self):

        collated_tokens = []

        # An alignment must be performed in order to ensure that the tokens for each line are parsed
        # @todo Refactor
        tokens = self.line['tokens']
        base_tokens = self.base_line['tokens']

        while len(tokens) > len(base_tokens):
            empty_token = Token('', tokens[-1]['index'])
            empty_token_data = json.loads(TokenJSONEncoder().encode(empty_token))
            base_tokens.append(empty_token_data)
        while len(tokens) < len(base_tokens):
            empty_token = Token('', base_tokens[-1]['index'])
            empty_token_data = json.loads(TokenJSONEncoder().encode(empty_token))
            tokens.append(empty_token_data)
        for token, base_token in zip(tokens, base_tokens):
            collated_tokens.append(CollatedToken( base_token, token ))

        self.tokens = collated_tokens
        self.unaligned_tokens = self.tokens

    def find_distance(self, base_line, line):

        distance = nltk_distance.edit_distance(base_line['value'], line['value'])
        return distance

    def values(self):
        return {
            'base_line': self.base_line,
            'value': self.line['value'],
            'index': self.index,
            'tokens': map(lambda token: token.values(), self.tokens),            
            'classes': self.line['classes'],
            'markup': self.line['markup']
        }

