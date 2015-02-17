
from nltk.tokenize.punkt import PunktWordTokenizer
import networkx as nx
import re
import nltk
import string

class TextToken:

    def __init__(seltf, ngram):

        self.value = ngram

class ElementToken:  

    def __init__(self, name=None, attrib=None, children=None, text=None, doc=None, **kwargs):

        if doc is not None:

            name = doc.xpath('local-name()')
            attrib = doc.attrib
            children = list(doc)
            text = string.join(list(doc.itertext())) if doc.text is not None else ''

        self.name = name
        self.attrib = attrib

        # Generate a string consisting of the element name and concatenated attributes (for comparison using the edit distance)
        # Note: the attributes *must* be order by some arbitrary feature

        self.value = '<' + self.name
        for attrib_name, attrib_value in self.attrib.iteritems():
            
            self.value += ' ' + attrib_name + '="' + attrib_value + '"'
        self.value += ' />'

        self.children = children

        self.text = text

# The Fragment Entity passed to the Juxta visualization interface
class Fragment:

    def __init__(self, tokens):

        self.value

class Tokenizer:

    def __init__(self):

        pass

    # Construct the parse tree
    # Each element is a node distinct from the 
    @staticmethod
    def parse(node):

        # Initialize an undirected graph for the tree, setting the root node to the lxml node
        token_tree = nx.Graph()
        token_tree_root = ElementToken(doc=node)

        # For the text of the node, use the PunktWordTokenizer to tokenize the text
        # Ensure that each tokenized n-gram is linked to the lxml token for the tree:
        #    o
        # /     \
        # n-gram n-gram

        # text_tokens = tokenizer.tokenize( token_tree_root.text )
        text_tokens = [ token_tree_root.text ]

        init_dist = 0

        # Introduce the penalty for stylistic or transcription elements
        # @todo This also requires some problematic restructuring of footnote and rendering elements (as these are *not* leaves)

        # text_token_edges = map(lambda token: (token_tree_root, TextToken(token)), text_tokens )
        text_token_edges = map(lambda token: (token_tree_root.value, token, { 'distance': init_dist }), text_tokens )
        # text_token_edges = map(lambda token: (token_tree_root, token), text_tokens )

        token_tree.add_edges_from(text_token_edges)

        children = list(node)
        
        # If the lxml has no more nodes, return the tree
        if len(children) == 0:

            return token_tree

        # ...otherwise, merge the existing tree with the sub-trees generated by recursion
        sub_trees = map(Tokenizer.parse, children)

        for sub_tree in map(Tokenizer.parse, children):

            token_tree = nx.compose(token_tree, sub_tree)
        return token_tree

    @staticmethod
    def diff(node_u, node_v):

        tree_u = Tokenizer.parse(node_u)
        tree_v = Tokenizer.parse(node_v)

        diff_tree = nx.Graph()

        # Assess the difference in tree structure
        # diff_tree = nx.difference(tree_u, tree_v)

        # Calculate the edit distance for each identical node between the trees

        # Retrieve the common edges
        # intersect_tree = nx.intersection(tree_u, tree_v)

        # Iterate through each edge
        # for edge in intersect_tree.edges(data=True):
        for u, v, data in tree_u.edges(data=True):

            # Only perform the edit distance for text nodes
            # edit_dist = nltk.metrics.distance(tree_u[u], tree_v[u])
            # (u, u, edit_dist)

            # text_nodes = filter( lambda e: e.__class__.__name__ != 'ElementToken', [u,v] )
            text_nodes = filter( lambda e: not re.match(r'^<', e), [u,v] )

            if len(text_nodes) > 1:

                raise Exception("Text nodes can not be linked to text nodes", text_nodes)
            elif len(text_nodes) == 0:

                # Comparing elements
                assert False
            else:
                
                text_node_u = string.join(text_nodes)
                elem_node_u = v if u == text_node_u else u
                nodes_u_dist = data['distance']

                # Retrieve the same text node from the second tree
                text_nodes_v = tree_v[elem_node_u].keys()
                
                text_node_v = string.join(text_nodes_v)
                nodes_v_dist = tree_v[elem_node_u][text_node_v]['distance']

                # Default to Punkt
                # tokenizer = PunktWordTokenizer()

                # Just add the edit distance
                edit_dist = nodes_u_dist + nodes_v_dist + nltk.metrics.distance.edit_distance(text_node_u, text_node_v)
                
                diff_tree.add_edge(elem_node_u, text_node_u, distance=edit_dist)
                pass

            pass

        # Generate the edit distance
        
        # Append the edge to the diff_tree, with the edit distance as the attribute

        return diff_tree
