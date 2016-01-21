
import string

from token import Token

class Line(object):

    def __init__(self, value, index, tokenizer, classes={}, markup={}):

        self.value = value
        self.index = index
        self.tokens = []
        self.tokenizer = tokenizer()
        self.classes = classes
        self.markup = markup

    def __unicode__(self):

        return unicode(self.value).encode('utf-8')

    def __str__(self):

        return self.__unicode__()

    def tokenize(self):

        self.tokens = []

        token_values = self.tokenizer.tokenize(self.value)
        
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
            token = Token(token_value, token_index, token_classes, token_markup)

            self.tokens.append(token)

class FootnoteLine(Line):

    def __init__(self, value, index, target_id, distance_from_parent, tokenizer, classes={}, markup={}):
        
        self.target_id = target_id
        self.distance_from_parent = distance_from_parent
        super(FootnoteLine, self).__init__(value, index, tokenizer=tokenizer, classes=classes, markup=markup)
