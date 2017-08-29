
import nltk
import json
# from ..text import Token, TokenJSONEncoder
from ..text import Token

class DifferenceToken(Token):

    def __init__(self, base_token, other_token):

        self.base_token = base_token
        # Work-around
        self.base_token.distance = 0

        super(DifferenceToken, self).__init__(other_token.value, other_token.index, other_token.classes, other_token.markup, other_token.pos)
        self.distance = self.find_distance()

    def find_distance(self):

        self.distance = nltk.metrics.distance.edit_distance(self.base_token.value, self.value)
        return self.distance

# This needs to be removed, and the circular dependency issue resolved
#
class TokenJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Token):
            return {
                'value': obj.value,
                'index': obj.index,
                'classes': obj.classes,
                'markup': obj.markup
                }
        return json.JSONEncoder.default(self, obj)

class DifferenceTokenJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, DifferenceToken):
            return {
                'base_token': json.loads(TokenJSONEncoder().encode(obj.base_token)),
                'value': obj.value,
                'index': obj.index,
                'classes': obj.classes,
                'markup': obj.markup
                }
        return json.JSONEncoder.default(self, obj)
