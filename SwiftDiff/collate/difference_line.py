import nltk

from ..text import Line, Token
from difference_token import DifferenceToken

class DifferenceLine(Line):

    def __init__(self, base_line, other_line, tokenizer):

        # self.other_line = other_line
        self.base_line = base_line
        self.distance = self.find_distance(base_line, other_line)

        self.position = ''
        self.uri = ''

        super(DifferenceLine, self).__init__(other_line.value, other_line.index, tokenizer=tokenizer, classes=other_line.classes, markup=other_line.markup)

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


                pass
            pass
        pass

        diff_tokens = []

        for token, base_token in zip(self._tokens, self.base_line.tokens):
            diff_tokens.append(DifferenceToken( base_token, token ))

        self.tokens = diff_tokens

    def tokenize(self):

        super(DifferenceLine, self).tokenize()

        # This shouldn't need to be invoked
        # @todo investigate and remove
        self.base_line.tokenize()

        diff_tokens = []

        # An alignment must be performed in order to ensure that the tokens for each line are parsed
        # @todo Refactor
        tokens = self.tokens
        base_tokens = self.base_line.tokens

        if len(tokens) > len(base_tokens):
            empty_token = Token('', self.tokens[-1].index)
            self.base_line.tokens.append(empty_token)
            # diff_tokens.append(DifferenceToken( empty_token, self.tokens[-1] ))
        elif len(tokens) < len(base_tokens):
            empty_token = Token('', self.base_line.tokens[-1].index)
            self.tokens.append(empty_token)
            # diff_tokens.append(DifferenceToken( self.base_token.tokens[-1], empty_token ))

        for token, base_token in zip(self.tokens, self.base_line.tokens):
            diff_tokens.append(DifferenceToken( base_token, token ))

        self._tokens = self.tokens
        self.tokens = diff_tokens
