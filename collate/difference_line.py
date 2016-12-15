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

    def align_d(self):
        """Aligns two lines of (potentially) unequal length
        """

        # Align the tokens
        base_tokens = self.tokens
        other_tokens = self.base_line.tokens

        if len(base_tokens) > len(other_tokens):

            # Insert padding at the beginning or end of the sequence
            empty_tokens = [ Token('', None) ] * (len(base_tokens) - len(other_tokens))
            while len(empty_tokens) > 0:

                # Don't attempt to match against the entire string
                # Needleman-Wunsch?
                # @todo There is probably a library for this
                if other_tokens[0] == base_tokens[1]:
                    other_tokens.insert(0, empty_tokens.pop())
                else:
                    other_tokens.append(empty_tokens.pop())
                pass
        elif len(base_tokens) > len(other_tokens):

            empty_tokens = [ Token('', None) ] * (len(other_tokens) - len(base_tokens))
            while len(empty_tokens) > 0:

                # empty_tokens.pop()
                # Don't attempt to match against the entire string
                # Needleman-Wunsch?
                # @todo There is probably a library for this
                if base_tokens[0] == other_tokens[1]:
                    base_tokens.insert(0, empty_tokens.pop())
                else:
                    base_tokens.append(empty_tokens.pop())
                pass
        pass

    def align(self):
        """Aligns two lines of (potentially) unequal length
        """

        for i, token in enumerate(self._tokens):
            if i < len(self.base_line.tokens) - 1:
                if self.base_line.tokens[i + 1].value == self._tokens[i].value:
                    self._tokens.insert( 0, Token('', None) )
                    self.base_line.tokens.append( Token('', None) )

        diff_tokens = []

        for token, base_token in zip(self._tokens, self.base_line.tokens):
            diff_tokens.append(DifferenceToken( base_token, token ))

        self.tokens = diff_tokens

    def tokenize(self):

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
