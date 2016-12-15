import nltk
from nltk.tag import pos_tag
nltk.download('maxent_treebank_pos_tagger')
import numpy

import string
import json

from token import Token, TokenJSONEncoder

class Line(object):

    def __init__(self, value, index, tokenizer, tagger, classes={}, markup={}, footnotes=[]):

        self.value = value
        self.index = index
        self.tokens = []
        self.tokenizer = tokenizer()
        self.tagger = tagger
        self.classes = classes
        self.markup = markup
        self.footnotes = footnotes

    def tokenize(self):
        """Tokenize the line
        """

        self.tokens = []
        token_values = self.tokenizer.tokenize(self.value)

        # Retrieve the POS tags
        # Classify the token in terms of the part-of-speech using a Perceptron-based tagger

        ## Disabling in order to test SPP-651
        # pos_tags = pos_tag(token_values)
        if self.tagger is None:
            pos_tags = []
        else:
            pos_tags = self.tagger.tag(token_values)

        line_value = self.value

        # Need to parse the classes
        for token_index, token_value in enumerate(token_values):

            # Filter for the classes
            _classes = filter(lambda _class: _class['start'] >= string.find(line_value, token_value) and _class['end'] <= string.find(self.value, token_value) + len(token_value), self.classes.itervalues())
            token_classes = map(lambda _class_key: _class_key, self.classes.iterkeys())

            # Filter for the markup
            token_markup = {}
            _markup = {}

            for tag_name, tag_list in self.markup.iteritems():

                for tag_items in tag_list:

                    markup_items = tag_items['markup']
                    range_items = tag_items['range']

#                    if range_items['start'] == string.find(line_value, token_value) and range_items['end'] <= string.find(line_value, token_value) + len(token_value) - 1:
                    if range_items['start'] == string.find(line_value, token_value):

                        _markup = token_markup.copy()
                        _markup.update(markup_items)
                        token_markup = _markup

                        # Replace
                        # line_value = ''.replace(line_value, token_value, '', 1)
            
            # Create the token


            if token_index in pos_tags:
                token = Token(token_value, token_index, token_classes, token_markup, pos_tags[token_index][-1])
            else:
                token = Token(token_value, token_index, token_classes, token_markup, None)

            self.tokens.append(token)

class FootnoteLine(Line):

    def __init__(self, value, index, target_id, distance_from_parent, tokenizer, tagger=None, classes={}, markup={}):
        
        self.target_id = target_id
        self.distance_from_parent = distance_from_parent
        super(FootnoteLine, self).__init__(value, index, tokenizer=tokenizer, tagger=tagger, classes=classes, markup=markup)

####

class LineJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Line):
            return {
                'value': obj.value,
                'index': obj.index,
                'tokens': map(lambda token: json.loads(TokenJSONEncoder().encode(token)), obj.tokens),
                'classes': obj.classes,
                'markup': obj.markup
                }
        return json.JSONEncoder.default(self, obj)
