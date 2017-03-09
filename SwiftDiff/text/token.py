import re
from string import punctuation
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
        self.normal_value = self.normalize_value()

    def normalize_value(self):

        normal_value = self.value
        normal_value = self.value.lower()

        r = re.compile(r'[{0}]+'.format(re.escape(punctuation)))
        normal_value = re.sub(r, '', normal_value)

        return normal_value

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
