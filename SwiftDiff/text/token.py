#import nltk
#from nltk.tag import pos_tag
#nltk.download('maxent_treebank_pos_tagger')
#import numpy
import re

class Token(object):

    def __init__(self, value, index, classes=[], markup={}):

        self.value = value
        self.index = index
        self.classes = classes
        self.markup = markup

        # Classify the token in terms of the part-of-speech using a perceptron tagger
#        self.pos = pos_tag(value)

        # Clean
        self.value = re.sub(r'_', '', self.value)
        self.value = re.sub('08\.', '', self.value)
        self.value = re.sub('8\.', '', self.value)
