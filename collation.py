
import re

class Collation:

    html_doc = """

"""

    def __init__(self, diff_tree):

        self.tree = diff_tree

        # The columnar matrix for the set of collated tokens
        self._values = []

        self.doc = self.parse()

    def parse(self):

        # Iterate through the tree in order to generate the values

        i=0
        for u,v,data in self.tree.edges(data=True):

            text = u if re.match(r'^<.+>$', v) else v
            xml = v if text is u else u

            # Avoid all non-lines
            if re.match(r'^<[lp]\s', xml):

                self._values.append([])

                # Be certain to index using the @n attribute
                n_match = re.match(r'^<[lp]\sn="(\d+)"', xml)
                if n_match:

                    print n_match
                    n = int(n_match.group(1))
                else:
                    
                    n=i

                distance = data['distance']
                rows = [n, text, distance]

                self._values[i] = rows
                i+=1

        # Sort by the n index
        self._values = sorted(self._values, key=lambda row: row[0])

    # @todo Replace by implementing the protocol for a container
    def __list__(self):

        return self._values

    def __xml__(self):

        return etree.tostring(self.doc)
