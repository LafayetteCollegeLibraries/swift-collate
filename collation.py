
import re

class Collation:

    html_doc = """

"""

    def __init__(self, diff_tree):

        self.tree = diff_tree

        # The columnar matrix for the set of collated tokens
        self._values = {}

        self.doc = self.parse()

    def parse(self):

        # Iterate through the tree in order to generate the values

        i=0
        for u,v,data in self.tree.edges(data=True):

            text = u if re.match(r'^<.+>$', v) else v
            xml = v if text is u else u

            # Avoid all non-lines
            if re.match(r'^<[lp]\s', xml):

                # print u
                # print v
                # print data

                # self._values.append([])

                # Be certain to index using the @n attribute
                n_match = re.match(r'^<[lp]\sn="(\d+)"', xml)
                if n_match:

                    n = int(n_match.group(1))
                else:
                    
                    n=i

                witness = data['witness']
                distance = data['distance']
                rows = {'witness': witness, 'number': n, 'text': text, 'distance': distance }

#                print rows
#                self._values[n] = rows
#                print self._values

                # Each line contains multiple witnesses
                if n in self._values:

                    # print self._values[n]
                    self._values[n].append(rows)
                    # print self._values[n]
                    # self._values[n] = self._values[n] + (rows,)
                else:

                    # print self._values
                    # print n
                    # self._values[n] = (rows,)
                    self._values[n] = [rows]

                i+=1

#        print self._values

        # Sort by the n index
        sorted_values = {}
        for n,row in self._values.iteritems():

            sorted_values[n] = sorted(row, key=lambda e: e['distance'])

        self._values = sorted_values

    # @todo Replace by implementing the protocol for a container
    def to_dict(self):

        return self._values

    def table(self):

        # token token token
        # token token token

        for row in self._values:

            
            pass

        pass

    def __xml__(self):

        return etree.tostring(self.doc)
