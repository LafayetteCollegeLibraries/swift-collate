# -*- coding: utf-8 -*-

import nltk
nltk.download('punkt')

import nltk.data

class PunktSentenceTokenizer(object):
    """A trained PunktSentenceTokenizer
    
    """

    def __init__(self):
        try:
            self.trained = nltk.data.load('tokenizers/punkt/english.pickle')
        except:
            raise "Could not train the Punkt sentence tokenizer"

    def tokenize(self, value):

        self.trained.tokenize(value)
        return self.trained.tokenize(value)
