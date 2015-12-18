
import nltk
from ..text import Token

class DifferenceToken(Token):

    def __init__(self, base_token, other_token):

        self.distance = self.find_distance(base_token, other_token)

        super(DifferenceToken, self).__init__(other_token.value, other_token.index, other_token.classes, other_token.markup)

    def find_distance(self, base_token, other_token):

        distance = nltk.metrics.distance.edit_distance(base_token.value, other_token.value)

        return distance
