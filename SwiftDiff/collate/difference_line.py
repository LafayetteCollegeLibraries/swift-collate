import nltk

from ..text import Line, Token, LineJSONEncoder
from difference_token import DifferenceToken, DifferenceTokenJSONEncoder
import json

class DifferenceLine(Line):

    def __init__(self, base_line, other_line, tokenizer, tagger=None):

        # self.other_line = other_line
        self.base_line = base_line
        self.distance = self.find_distance(base_line, other_line)

        self.position = ''
        # self.uri = ''
        self.id = ''

        super(DifferenceLine, self).__init__(other_line.value, other_line.index, tokenizer=tokenizer, tagger=tagger, classes=other_line.classes, markup=other_line.markup, footnotes=other_line.footnotes)

    def find_distance(self, base_line, other_line):

        distance = nltk.metrics.distance.edit_distance(base_line.value, other_line.value)

        return distance

    def tokenize(self, retokenize = True):

        if retokenize:
            # Disabling for SPP-651
            super(DifferenceLine, self).tokenize()

            # This shouldn't need to be invoked
            # @todo investigate and remove

            # Disabling for SPP-651
            self.base_line.tokenize()

        diff_tokens = []

        # An alignment must be performed in order to ensure that the tokens for each line are parsed
        # @todo Refactor
        tokens = self.tokens
        base_tokens = self.base_line.tokens

        while len(self.tokens) > len(self.base_line.tokens):
            empty_token = Token('', self.tokens[-1].index)
            self.base_line.tokens.append(empty_token)
        while len(self.tokens) < len(self.base_line.tokens):
            empty_token = Token('', self.base_line.tokens[-1].index)
            self.tokens.append(empty_token)
        for token, base_token in zip(self.tokens, self.base_line.tokens):
            diff_tokens.append(DifferenceToken( base_token, token ))

        self._tokens = self.tokens
        self.tokens = diff_tokens

class DifferenceLineJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, DifferenceLine):
            return {
                'base_line': json.loads(LineJSONEncoder().encode(obj.base_line)),
                'value': obj.value,
                'index': obj.index,
                'tokens': map(lambda token: json.loads(DifferenceTokenJSONEncoder().encode(token)), obj.tokens),
                'classes': obj.classes,
                'markup': obj.markup
                }
        return json.JSONEncoder.default(self, obj)
