
import re
import json

from tokenizer import TextToken

class Collation:

    html_doc = """

"""

    def __init__(self, diff_tree):

        self.tree = diff_tree

        # The columnar matrix for the set of collated tokens
        self._values = {'lines': {}, 'witnesses': {}}

        self.doc = self.parse()

    def parse(self):

        # Iterate through the tree in order to generate the values

        i=0
        for u,v,data in self.tree.edges(data=True):

#            text_token = u if re.match(r'^<.+>$', v) else v
            text_token = u if isinstance(u, TextToken) else v
            xml = v if text_token is u else u

            # Work-around implemented in order to ensure that each text node is unique
            # text = re.sub(r'^__?', '', text)
            text = text_token.value

            # Avoid all non-lines
            if re.match(r'^<[lp]\s', xml):

                # self._values.append([])

                # Be certain to index using the @n attribute
                n_match = re.match(r'^<[lp]\sn="(\d+)"', xml)
                if n_match:

                    n = int(n_match.group(1))
                else:
                    
                    n=i

                feature = data['feature']
                position = data['position'] if 'position' in data else None

                witness = data['witness']
                distance = data['distance']
                rows = {'witness': witness, 'number': n, 'text': text, 'distance': distance, 'position': position }

#                print rows
#                self._values[n] = rows
#                print self._values

                # Structuring ngrams within any given line
                if feature == 'ngram':

                    # Firstly, index all ngrams by their related witnesses
                    if witness in self._values['witnesses']:

                        self._values['witnesses'][witness][feature].append(rows)
                    else:

                        self._values['witnesses'][witness] = { feature: [rows] }

                    # Structure the data in order to ensure that each token is mapped to a boolean value indicating whether or not the token is present within the line
                    if n in self._values['lines']:

                        # Ensure that each line has ngrams related to it
                        if not feature in self._values['lines'][n]:
                            
                            self._values['lines'][n][feature] = { witness: { position: text } }

                        # print 'trace10'
                        # print position
                        # print self._values['lines'][n][feature]

                        elif not witness in self._values['lines'][n][feature]:

                            self._values['lines'][n][feature][witness] = { position: text }
                        else:

                            # Prepend any missing tokens
                            # if position > 0 and not position - 1 in self._values['lines'][n][feature][witness]:

                            #    self._values['lines'][n][feature][witness][position - 1] = ''

                            self._values['lines'][n][feature][witness][position] = text
                    else:

                        self._values['lines'][n] = { feature: { witness: { position: text } } }

                else:
                    # All other features within any given line

                    # print 'trace6'

                    # Each line contains multiple witnesses
                    if n in self._values['lines']:

                        if not feature in self._values['lines'][n]:
                            
                            self._values['lines'][n][feature] = []
                            self._values['lines'][n][feature].append(rows)
                            
                            # print self._values[n]
                            # self._values[n] = self._values[n] + (rows,)
                        else:
                            
                            # print self._values
 
                            # print n
                            # self._values[n] = (rows,)
                            
                            # self._values[n] = [rows]
                            self._values['lines'][n][feature].append(rows)
                            
                            #                print 'line: ' + str(n)
                            #                print self._values[n]
                    else:

                        self._values['lines'][n] = {feature: [rows]}


                i+=1

#        print 'trace3'
#        print self._values.keys()
#        print self._values['lines'][2]['ngram']
#        print 'trace4'

        # Sort by the n index
        sorted_values = {'lines': {}, 'witnesses': {}}

        for doc_feature in self._values:

#            print 'trace4'
#            print feature
#            print self._values[doc_feature]

            for n,value in self._values[doc_feature].iteritems():

#                print 'trace5'
#                print n
#                print value

#                values = value[feature]
#                print values
#                print 'trace6'
#                print sorted_values
                
                if not n in sorted_values[doc_feature]:

                    sorted_values[doc_feature][n] = {}
                    
                    for feature,row in value.iteritems():

#                        print 'trace8'
#                        print n
#                        print feature
#                        print row
#                        print 'trace9'
#                        print sorted_values
                        
                        # sorted_values[doc_feature][n] = {}
                        if not feature in sorted_values[doc_feature][n]:

#                            print 'trace8'
                            
                            sorted_values[doc_feature][n][feature] = []
                            
                            if feature == 'ngram':

                                # print 'trace9'
                                # print doc_feature
                                # print n
                                # print feature

                                # print row

                                if doc_feature == 'lines':
                                    
                                    # pass
                                    # sorted_values[doc_feature][n][feature].append(row)
                                    # print 'trace13'
                                    # print row

                                    sorted_line_ngrams = {}
                                    max_line_ngrams = max( map(lambda line_ngrams: max(map(lambda ngram_pos: ngram_pos, line_ngrams)), row.values()) ) + 1
                                    # print 'trace14'
                                    # print max_line_ngrams

                                    for line_ngram_source, line_ngrams in row.iteritems():

                                        sorted_ngrams = [''] * max_line_ngrams
                                        for ngram_pos, ngram in line_ngrams.iteritems():

                                            sorted_ngrams[ngram_pos] = ngram

                                        sorted_line_ngrams[line_ngram_source] = sorted_ngrams
                                    
                                    sorted_values[doc_feature][n][feature] = sorted_line_ngrams
                                else:

                                    sorted_values[doc_feature][n][feature] = sorted(row, key=lambda e: e['position'])
                                    # print sorted(row, key=lambda e: e['number'])
                            else:

                                sorted_values[doc_feature][n][feature] = sorted(row, key=lambda e: e['distance'])

        self._values = sorted_values

    # @todo Replace by implementing the protocol for a container
    def values(self):

        return self._values

    def __unicode__(self):

        return json.dumps(self.values())

    def __str__(self):

        return unicode(self)

    def table(self):

        # token token token
        # token token token

        for row in self._values:

            
            pass

        pass

    def __xml__(self):

        return etree.tostring(self.doc)
