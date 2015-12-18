import nltk

from ..text import Line
from difference_token import DifferenceToken

class DifferenceLine(Line):

    def __init__(self, base_line, other_line, tokenizer):

        self.other_line = other_line
        self.distance = self.find_distance(base_line, other_line)

        self.position = ''
        self.uri = ''

        super(DifferenceLine, self).__init__(base_line.value, base_line.index, tokenizer=tokenizer, classes=base_line.classes, markup=base_line.markup)

    def find_distance(self, base_line, other_line):

        distance = nltk.metrics.distance.edit_distance(base_line.value, other_line.value)

        return distance

    def tokenize(self):

        super(DifferenceLine, self).tokenize()
        self.other_line.tokenize()

        diff_tokens = []

        # An alignment must be performed in order to ensure that the tokens for each line are parsed
        base_tokens = self.tokens
        other_tokens = self.other_line.tokens

        if len(base_tokens) > other_tokens:

            # Search for the terms
            for i, other_token in enumerate(other_tokens):

                # Attempt to find the token
#                index = string.find(self.value, other_token)
#                if index > -1:

#                    pass
                
                pass
            
            pass
        elif len(base_tokens) < other_tokens:

            # 
            pass

        for base_token, other_token in zip(base_tokens, other_tokens):
            diff_tokens.append(DifferenceToken(base_token, other_token))

        self.tokens = diff_tokens
