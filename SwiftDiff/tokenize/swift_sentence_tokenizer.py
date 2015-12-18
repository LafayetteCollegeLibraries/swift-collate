# -*- coding: utf-8 -*-

import re

class SwiftSentenceTokenizer(object):
    """The sentence tokenizer specialized for the Swift Poems Project
    
    """

    def tokenize(self, value):

        # For handling cases related to non-breaking spaces inserted within strings (e. g. "I 'd")
        # Please see SPP-269
        value = re.sub(r"(.)[\s ]('.)", "\\1\\2", value)

        # tokens = value.split()
        tokens = []

        

        for token in value.split():

#            if re.match(r'.*<.+?>.*', token):

#                split_tokens = re.split(r'.(?=<)', token)
#                for split_token in split_tokens:

#                    for escaped_token in re.split(r'(?=>).', split_token):
#                        escaped_token = re.sub('<(.+)', '\\1', escaped_token)
#                        tokens.append(escaped_token)
#            else:
#                tokens.append(token)
            tokens.append(token)

        return tokens

class SwiftCleanSentenceTokenizer(SwiftSentenceTokenizer):

    def tokenize(self, value):

        # Handling for \\ tokens
        value = re.sub(r"\\(.+?)\\", "", value)

        super(SwiftCleanSentenceTokenizer, self).tokenize(value)
