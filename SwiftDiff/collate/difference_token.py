
import nltk
from ..text import Token

class DifferenceToken(Token):

    def __init__(self, base_token, other_token):

        self.base_token = base_token
        # Work-around
        self.base_token.distance = 0

        self.distance = self.find_distance(base_token, other_token)

        super(DifferenceToken, self).__init__(other_token.value, other_token.index, other_token.classes, other_token.markup, other_token.pos)

    def find_distance(self, base_token, other_token):

        distance = nltk.metrics.distance.edit_distance(base_token.value, other_token.value)

        return distance
