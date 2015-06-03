
import re
import json
from operator import itemgetter

from tokenizer import TextToken

class Collation:

    html_doc = """

"""

    def __init__(self, diff_tree):

        self.tree = diff_tree

        # The columnar matrix for the set of collated tokens
        self._values = {'lines': {}, 'witnesses': {}}

        self.doc = self.parse()

    # Sort the collation (in order to structure the JSON Objects)
    # @param line_ngram_distances The distances of ngrams related to each line
    #
    def sort(self, line_ngram_distances):

        # @author griffinj@lafayette.edu
        # Sorting functionality
        # The following structures the collation tree in such a manner as to ensure that tokens and lines are ordered by their related witnesses

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

#                        print 'TRACE8'
#                        print n
#                        print feature
#                        print row
#                        print 'trace9'
#                        print sorted_values
                        
                        # sorted_values[doc_feature][n] = {}
                        if not feature in sorted_values[doc_feature][n]:

#                            print 'trace8'
                            
                            sorted_values[doc_feature][n][feature] = []

                            # Ordering ngrams by line
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

                                    # Map each Dict item...
                                    _line_ngrams = [{'witness': witness, 'line_ngrams': v, 'order': witness, 'distances': []} for witness,v in sorted_line_ngrams.items()]
                                    # ordered_line_ngrams = [{}] * (len(_line_ngrams) + 1)

                                    # ...and sort them:
                                    ordered_line_ngrams = []
                                    unordered_line_ngrams = []
                                    
                                    for line_ngram in _line_ngrams:

                                        if line_ngram['witness'] == 'base':

                                            ordered_line_ngrams = ordered_line_ngrams + [line_ngram]
                                        elif line_ngram['witness'] == 'common':

                                            ordered_line_ngrams = [line_ngram] + ordered_line_ngrams
                                        else:

                                            unordered_line_ngrams.append(line_ngram)

                                        # SPP-177
                                        # Work-around
                                        # @todo Refactor
                                            
                                        # Index by line, witness, position
                                        # sorted_values[doc_feature][n]['ngrams_distances'][line_ngram['witness']] = map(lambda line_ngram: line_ngram.distance, line_ngram['line_ngrams'])

                                    # ordered_line_ngrams = ordered_line_ngrams[0:1] + sorted(unordered_line_ngrams, key=itemgetter('witness')) + ordered_line_ngrams[1:]
                                    ordered_line_ngrams = ordered_line_ngrams[0:2] + sorted(unordered_line_ngrams, key=itemgetter('witness'))

                                    sorted_values[doc_feature][n]['ngrams_sorted'] = ordered_line_ngrams
                                    sorted_values[doc_feature][n]['ngrams_distances'] = line_ngram_distances[n]
                                else:

                                    sorted_values[doc_feature][n][feature] = sorted(row, key=lambda e: e['position'])
                            else:

                                sorted_values[doc_feature][n][feature] = sorted(row, key=lambda e: e['distance'])

        self._values = sorted_values

    # Iterate through each edge of the directed graph, and generate the values for the text tokens
    #
    def parse(self):

        # Iterate through the tree in order to generate the values

#        print 'trace2: nodes for <lg n="1"/l n="3" />'
#        print self.tree['<lg n="1"/l n="3" />']

        line_ngram_distances = {}

        i=0
        for u,v,data in self.tree.edges(data=True):

            # Determine which of the nodes are text tokens or XML elements
            text_token = u if isinstance(u, TextToken) else v
            text = text_token.value

            xml = v if text_token is u else u

            # This ensures that only <l> and <p> elements are analyzed (from the standpoint of syntactic and semantic relationships)
            # Further, only lines bearing numbers are analyzed
            #
            # <lg/l n="2" />
            # <lg n="1"/l n="3" />
            # if re.match(r'^[lp]\s', xml):
            # if re.match(r'^<[lp]\s', xml):
            n_match = re.match(r'.+?[lp]\sn="(\d+)"', xml)
            if n_match:

                # self._values.append([])

                # Be certain to index using the @n attribute
                # <lg/l n="2" />
#                n_match = re.match(r'^[lp]\sn="(\d+)"', xml)
                # n_match = re.match(r'^<lg\sn="(\d+)"/[lp]\sn="(\d+)"', xml)
                
                if n_match:

                    # stanza_n = int(n_match.group(1))
                    # line_n = int(n_match.group(2))
                    # n = int(n_match.group(2))

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

#                    if n == 3 and witness == 'common':
#                        print 'trace: line' + str(n)
#                        print { witness: { position: text } }

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

                    # Handling for the edit distances for each token
                    # Implemented for SPP-177
                    # @todo Refactor

#                    print 'TRACE ADDING NGRAM DISTANCE'
#                    print { position: distance }

                    # Index by line, witness, position
                    if n in line_ngram_distances:

                        if witness in line_ngram_distances[n]:

                            line_ngram_distances[n][witness][position] = distance
                        else:

                            line_ngram_distances[n][witness] = { position: distance }
                    else:

                        line_ngram_distances[n] = { witness: { position: distance } }

#                    print 'TRACE ADDING NGRAM DISTANCE2'
#                    print line_ngram_distances

                else:

                    # All other features within any given line
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

                            if self._values['lines'][n][feature].count(rows) == 0:

                                self._values['lines'][n][feature].append(rows)
                            
                            #                print 'line: ' + str(n)
                            #                print self._values[n]
                    else:

                        self._values['lines'][n] = {feature: [rows]}


                i+=1

        return self.sort(line_ngram_distances)

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
