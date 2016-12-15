import re
import json

class Token(object):

    def __init__(self, value, index, classes=[], markup={}, pos=None):

        self.value = value
        self.index = index
        self.classes = classes
        self.markup = markup
        self.distance = 0

        # Clean
        self.value = re.sub(r'_', '', self.value)
        self.value = re.sub('08\.', '', self.value)
        self.value = re.sub('8\.', '', self.value)

        self.pos = pos

####

class TokenJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Token):
            return {
                'value': obj.value,
                'index': obj.index,
                'classes': obj.classes,
                'markup': obj.markup,
                'distance': obj.distance
                }
        return json.JSONEncoder.default(self, obj)
