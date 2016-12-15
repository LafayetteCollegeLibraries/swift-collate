# -*- coding: utf-8 -*-

from nltk.tokenize.punkt import PunktWordTokenizer
# from nltk.tokenize import TreebankWordTokenizer
import networkx as nx
import re
import nltk
import string
from copy import deepcopy
from lxml import etree
import urllib

from difflib import ndiff

from swift_sentence_tokenizer import SwiftSentenceTokenizer
from punkt_sentence_tokenizer import PunktSentenceTokenizer

class Tokenizer:

    def __init__(self):

        pass

    # Construct a Document sub-tree consisting solely of stanzas or paragraphs from any given TEI-encoded text
    @staticmethod
    def parse_stanza(resource):

        response = urllib.urlopen(resource)
        data = response.read()

        try:

            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()
        except Exception as inst:

            # doc = etree.fromstring('<?xml version="1.0" encoding="utf-8"?><TEI xmlns="http://www.tei-c.org/ns/1.0" xml:lang="en"><text><body><div type="book"><div n="006-35D-" type="poem"><lg n="1"></lg></div></div></body></text></TEI>')
            # elems = doc.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            # elem = elems.pop()
            return None

        return elem

    @staticmethod
    def clean(data):
        """Clean the data from a TEI Document

        :param data: The raw XML from the TEI Document.
        :type data: str.
        """

        #data = re.search(r'«MDUL»', 'hi rend="underline"')
        #return data

        mode_code_pattern = re.compile('<«MDUL»>', re.M)
        data = re.sub(mode_code_pattern, '<hi rend="underline">', data)
        mode_code_pattern = re.compile('</«MDUL»>', re.M)
        data = re.sub(mode_code_pattern, '</hi>', data)

        # <«MDSD»>
        mode_code_pattern = re.compile('<«MDSD»>', re.M)
        data = re.sub(mode_code_pattern, '', data)
        mode_code_pattern = re.compile('</«MDSD»>', re.M)
        data = re.sub(mode_code_pattern, '', data)

        # <«MDSU»>
        mode_code_pattern = re.compile('<«MDSU»>', re.M)
        data = re.sub(mode_code_pattern, '', data)
        mode_code_pattern = re.compile('</«MDSU»>', re.M)
        data = re.sub(mode_code_pattern, '', data)

        # «FN1·
        mode_code_pattern = re.compile('<«FN1·>', re.M)
        data = re.sub(mode_code_pattern, '<note place="foot">', data)
        mode_code_pattern = re.compile('</«FN1·>', re.M)
        data = re.sub(mode_code_pattern, '</note>', data)

        return data

    @staticmethod
    def parse_content(data):

        data = Tokenizer.clean(data)
        
        try:
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:text', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

            # Append the <title> elements for the purposes of analysis
            title_elems = doc.xpath('//tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem.extend(title_elems)
        except Exception as ex:
            print ex.message
            return None
        return elem

    @staticmethod
    def parse_text(resource):

        response = urllib.urlopen(resource)
        data = response.read()

        # @todo Identify where this fails
        # data = clean(data)
#        if resource == '/var/lib/spp/tei/sources/0202/640-0202.tei.xml':

#            print resource
        mode_code_pattern = re.compile('<«MDUL»>', re.M)
        data = re.sub(mode_code_pattern, '<hi rend="underline">', data)
        mode_code_pattern = re.compile('</«MDUL»>', re.M)
        data = re.sub(mode_code_pattern, '</hi>', data)

        # <«MDSD»>
        mode_code_pattern = re.compile('<«MDSD»>', re.M)
        data = re.sub(mode_code_pattern, '', data)
        mode_code_pattern = re.compile('</«MDSD»>', re.M)
        data = re.sub(mode_code_pattern, '', data)

        # <«MDSU»>
        mode_code_pattern = re.compile('<«MDSU»>', re.M)
        data = re.sub(mode_code_pattern, '', data)
        mode_code_pattern = re.compile('</«MDSU»>', re.M)
        data = re.sub(mode_code_pattern, '', data)

        # «FN1·
        mode_code_pattern = re.compile('<«FN1·>', re.M)
        data = re.sub(mode_code_pattern, '<note place="foot">', data)
        mode_code_pattern = re.compile('</«FN1·>', re.M)
        data = re.sub(mode_code_pattern, '</note>', data)

        #
        # xml:id="spp-545-07G1-footnote-headnote-2"
#        mode_code_pattern = re.compile(' xml:id=".+?"', re.M)
#        data = re.sub(mode_code_pattern, '', data)

#        mode_code_pattern = re.compile(' target=".+?"', re.M)
#        data = re.sub(mode_code_pattern, '', data)

        try:
            doc = etree.fromstring(data)
            elems = doc.xpath('//tei:text', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem = elems.pop()

            # Append the <title> elements for the purposes of analysis
            title_elems = doc.xpath('//tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            elem.extend(title_elems)
        except Exception as ex:
            print ex.message
            return None
        return elem

    @staticmethod
    def parse_poem(resource):

        doc = parse_text(resource)
        return Poem(doc)
        pass

    # Parsing for titles within the tree for a given text node
    # @todo Refactor as TextTree.titles.parse()
    #
    @staticmethod
    def text_tree_titles_parse(text_node):

        # @todo Refactor
        #

        # Append a stanza for titles
        last_stanza_elems = text_node.xpath("//tei:lg[last()]", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        if len(last_stanza_elems) == 0:
            raise Exception('No <tei:lg> elements could be found within this node')
        last_stanza_elem = last_stanza_elems[-1]

        # Initialize the elements for the titles
        #
        title_container_stanza_elem = etree.SubElement(last_stanza_elem.getparent(), "lg", {'n': '1-titles', 'type': 'stanza'}, {'tei': 'http://www.tei-c.org/ns/1.0'})
        title_container_stanza_elems = [title_container_stanza_elem]

        # Initialize the indices for the titles
        title_container_stanza_index = 1
        title_line_index = 1

        # Iterate through all of the <head> elements as titles
        for title in text_node.xpath("//tei:title", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

            # Create the <l> element serving as a container for the <head> element
            title_line = etree.SubElement(title_container_stanza_elem, "l", {'n': str(title_line_index)}, {'tei': 'http://www.tei-c.org/ns/1.0'})
            title_line.text = ''.join(title.itertext())
            
            # Ensure that all text trailing the title element is preserved
            parent = title.getparent()

            parent_text = '' if parent.text is None else parent.text
            title_tail = '' if title.tail is None else title.tail
            parent.text = parent_text + title_tail

            # Titles are not to be removed, but instead, are to be appended following each line
            # node.append( deepcopy(title) )

            # Remove the title itself
            # title.getparent().remove(title)

            title_line_index += 1

        return title_container_stanza_elems

    # Parsing for headnotes within the tree for a given text node
    # @todo Refactor as TextTree.headnotes.parse()
    #
    @staticmethod
    def text_tree_headnotes_parse(text_node):

        # @todo Refactor
        #

        # Append a stanza for headnotes
        last_stanza_elems = text_node.xpath("//tei:lg[last()]", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        if len(last_stanza_elems) == 0:

            raise Exception('No <tei:lg> elements could be found within this node')
        last_stanza_elem = last_stanza_elems[-1]

        # Initialize the elements for the headnotes
        #
        headnote_container_stanza_elem = etree.SubElement(last_stanza_elem.getparent(), "lg", {'n': '1-headnotes', 'type': 'stanza'}, {'tei': 'http://www.tei-c.org/ns/1.0'})
        headnote_container_stanza_elems = [headnote_container_stanza_elem]

        # Initialize the indices for the headnotes
        headnote_container_stanza_index = 1
        headnote_line_index = 1

        # Iterate through all of the <head> elements as headnotes
        for headnote in text_node.xpath("//tei:head/tei:lg/tei:l", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

            # Be certain to index each headnote by stanza
            parent_stanza_indices = headnote.xpath('../../@n')

            if len(parent_stanza_indices) == 0:

                raise Exception("Could not retrieve the stanza index for a given headnote")

            parent_stanza_index = parent_stanza_indices[-1]

            # Retrieve the stanza identifier of the current stanza element
            container_stanza_index = headnote_container_stanza_elem.get('n').split('-headnotes')[0]

            # If the current stanza identifier refers to another stanza, create a new stanza
            if parent_stanza_index != container_stanza_index:

                headnote_container_stanza_index += 1
                headnote_container_stanza_elem = etree.SubElement(last_stanza_elem.getparent(), "lg", {'n': str(headnote_container_stanza_index) + '-headnotes', 'type': 'stanza' }, {'tei': 'http://www.tei-c.org/ns/1.0'})
                headnote_line_index = 1
                headnote_container_stanza_elems.append(headnote_container_stanza_elem)

            # Ensure that the @n attribute preserves that this is a footnote
            headnote_line_n = str(headnote_line_index) + '-headnotes'

            # Create the <l> element serving as a container for the <head> element
            headnote_line = etree.SubElement(headnote_container_stanza_elem, "l", {'n': headnote_line_n }, {'tei': 'http://www.tei-c.org/ns/1.0'})
            headnote_line.text = ''.join(headnote.itertext())
            
            # Ensure that all text trailing the headnote element is preserved
            parent = headnote.getparent()

            parent_text = '' if parent.text is None else parent.text
            headnote_tail = '' if headnote.tail is None else headnote.tail
            parent.text = parent_text + headnote_tail

            # Headnotes are not to be removed, but instead, are to be appended following each line
            # node.append( deepcopy(headnote) )

            # Remove the headnote itself
            # headnote.getparent().remove(headnote)

            headnote_line_index += 1

        return headnote_container_stanza_elems

    # Parsing for footnotes within the tree for a given text node
    # @todo Refactor as TextTree.footnotes.parse()
    #
    @staticmethod
    def text_tree_footnotes_parse(text_node):

        # Structure a "footnote" stanza specifically for the parsing of footnotes
        # Resolves SPP-180
        #

        # Append a stanza for footnotes
        last_stanza_elems = text_node.xpath("//tei:lg[last()]", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        if len(last_stanza_elems) == 0:

            raise Exception('No <tei:lg> elements could be found within this node')
        last_stanza_elem = last_stanza_elems[-1]

        footnote_container_stanza_elem = etree.SubElement(last_stanza_elem.getparent(), "lg", {'n': '1-footnotes', 'type': 'stanza'}, {'tei': 'http://www.tei-c.org/ns/1.0'})
        footnote_container_stanza_elems = [footnote_container_stanza_elem]

#        footnote_container_stanza_elem = etree.Element("lg", {'n': '1-footnotes'}, {'tei': 'http://www.tei-c.org/ns/1.0'})
#        last_stanza_elems[0]

        # footnote_container_stanza_elem['n'] = '1-footnotes'
        footnote_container_stanza_index = 1
        footnote_line_index = 1

        for footnote in text_node.xpath("//tei:note[@place='foot']", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

            # Be certain to index each footnote by stanza
            parent_stanza_indices = footnote.xpath('../../@n')

            if len(parent_stanza_indices) == 0:

                raise Exception("Could not retrieve the stanza index for a given footnote")

            parent_stanza_index = parent_stanza_indices[-1]

            # Retrieve the stanza identifier of the current stanza element
            container_stanza_index = footnote_container_stanza_elem.get('n').split('-footnotes')[0]

            # Generate the stanza identifier of the current footnote
            # stanza = parent_stanza_elems[0] + '-footnotes'

            # If the current stanza identifier refers to another stanza, create a new stanza
            if parent_stanza_index != container_stanza_index:

                footnote_container_stanza_index += 1
                footnote_container_stanza_elem = etree.SubElement(last_stanza_elem.getparent(), "lg", {'n': str(footnote_container_stanza_index) + '-footnotes', 'type': 'stanza' }, {'tei': 'http://www.tei-c.org/ns/1.0'})
                footnote_line_index = 1
                footnote_container_stanza_elems.append(footnote_container_stanza_elem)

            # Ensure that the @n attribute preserves that this is a footnote
            footnote_line_n = str(footnote_line_index) + '-footnotes'

            # Create the <l> element serving as a container for the <note> element
            footnote_line = etree.SubElement(footnote_container_stanza_elem, "l", {'n': footnote_line_n}, {'tei': 'http://www.tei-c.org/ns/1.0'})
            # footnote_line.append(deepcopy(footnote))
            # footnote_line.extend(list(footnote))
            footnote_line.text = ''.join(footnote.itertext())
            # footnote_line['n'] = footnote_line_index

            # Append the footnote to the stanza element
            # footnotes.append(deepcopy(footnote))
            # footnote_container_stanza_elem.append(deepcopy(footnote_line))

            # Ensure that all text trailing the footnote element is preserved
            parent = footnote.getparent()

            parent_text = '' if parent.text is None else parent.text
            footnote_tail = '' if footnote.tail is None else footnote.tail
            parent.text = parent_text + footnote_tail

            # Footnotes are not to be removed, but instead, are to be appended following each line
            # node.append( deepcopy(footnote) )

            # Remove the footnote itself
            # footnote.getparent().remove(footnote)

            footnote_line_index += 1
    
        # return text_node
        return footnote_container_stanza_elems

    # Construct the Document tree for tei:text elements
    # The output is passed to either Tokenizer.diff() or Tokenizer.stemma()
    # This deprecates Tokenizer.parse()
    # The root node should have one or many <lg> child nodes
    @staticmethod
    def text_tree(text_node, name=''):

        # Handling for the following must be undertaken here:
        # * footnotes
        # * headnotes
        # * titles

        # Initially extract the titles
        titles_lg_nodes = Tokenizer.text_tree_titles_parse(text_node)
        lg_nodes = titles_lg_nodes

        # Next, extract the headnotes
        headnotes_lg_nodes = Tokenizer.text_tree_headnotes_parse(text_node)

        # lg_nodes = headnotes_lg_nodes
        lg_nodes.extend(headnotes_lg_nodes)

        # Restructure the text_node in order to handle footnotes
        footnotes_lg_nodes = Tokenizer.text_tree_footnotes_parse(text_node)

        lg_nodes.extend( text_node.xpath('//tei:lg', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) )
        lg_nodes.extend(footnotes_lg_nodes)

        if not lg_nodes:

            raise Exception("Could not retrieve any <lg> nodes for the following TEI <text> element: " + etree.tostring(text_node))

        token_tree = nx.Graph()
        token_tree.name = name

        for lg_node in lg_nodes:

            lg_tree = Tokenizer.parse(lg_node, name)
            token_tree = nx.compose(token_tree, lg_tree)

        return token_tree

    @staticmethod
    def parse_child(child):
        
        # Recurse for nested <hi> elements
        descendents = list(child.iterchildren())

        if len(descendents) == 0:

            child_text = child.text if child.text is not None else ''
        else:
        
            child_text = (child.text if child.text is not None else '') + string.join(map(Tokenizer.parse_child, descendents))

        child_tail = child.tail if child.tail is not None else ''

        output = child_text + child_tail

        if child.xpath('local-name()') == 'gap':

            output = child.xpath('local-name()').upper() + u"_ELEMENT" + child_tail

        elif child.get('rend'):

            rend_value = child.get('rend')
            rend_value = re.sub(r'\s', '-', rend_value)
            rend_value = rend_value.upper()

            # Filtering against a list of known markup
            if rend_value not in ['SMALL-TYPE-FLUSH-LEFT']:

                output = rend_value + u"_CLASS_OPEN" + child_text + rend_value + u"_CLASS_CLOSED" + child_tail

        return output

    # Construct the Document tree
    # The root node should be a <lg> node
    @staticmethod
    def parse(node, name=''):

        # Initialize an undirected graph for the tree, setting the root node to the lxml node
        token_tree = nx.Graph()

        token_tree.name = name

        # Parsing must be restricted to the '<l>' and '<p>' depth
        # @todo Refactor
        if node.xpath('local-name()') not in ['l']:

            children = list(node)
        
            # If the lxml has no more nodes, return the tree
            if len(children) == 0:

                return token_tree

            sub_trees = map(Tokenizer.parse, children)

            for sub_tree in map(Tokenizer.parse, children):

                token_tree = nx.compose(token_tree, sub_tree)

            return token_tree

        parent = node.getparent()  # Filter for stanzas within <lg @type="stanza"> or <lg type="verse-paragraph">
        if parent.get('type') != 'stanza' and parent.get('type') != 'verse-paragraph':

            return token_tree

        # Parsing node content
        #
        node_tail = '' if node.tail is None else node.tail
        node_text_head = unicode(node.text) if node.text is not None else ''
        node_text = node_text_head + string.join(map( Tokenizer.parse_child, list(node.iterchildren())), '') + node_tail
        node.text = node_text

#        node_markup = etree.tostring(node)
#        for feature in [{'xml': '<hi rend="italic">', 'text_token': 'italic'},
#                        {'xml': '<hi rend="display-initial">', 'text_token': 'display-initial'},
#                        {'xml': '<hi rend="underline">', 'text_token': 'underline'},
#                        {'xml': '<gap>', 'text_token': 'gap'}]:

#            feature_xml = feature['xml']

#            node_markup = re.sub(feature_xml + '(.+?)' + '</hi>', u"_CLASS_OPEN\\1_CLASS_CLOSED", node_markup)

#            new_node = etree.fromstring(node_markup)
            # text = string.join(list(new_node.itertext())) if new_node.text is not None else ''
#            node.text = string.join(list(new_node.itertext())) if new_node.text is not None else ''

        # Footnotes are not to be removed, but instead, are to be appended following each line

        # Store the footnotes within a separate tree for comparison
        footnote_tree = etree.fromstring('''
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <text>
    <body>
      <div1 type="book">
	<div2 type="poem">
	  <lg n="1">
	    <l n="1" />
	  </lg>
	</div2>
      </div1>
    </body>
  </text>
</TEI>''')

        # Structure a "footnote" stanza specifically for the parsing of footnotes
        # Resolves SPP-180
        #
        for footnote in node.xpath("//tei:note[@place='foot']", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

            # Be certain to index each footnote by stanza
            footnote_container_stanza_elems = footnote.xpath('../../@n')

            # When the tei:lg@n value is not specified, assume this to lie within the first stanza
            footnote_stanza = '1-footnotes'
            if len(footnote_container_stanza_elems) > 0:

                footnote_stanza = footnote_container_stanza_elems[0] + '-footnotes'

            # Find or add a stanza for the footnotes
            
            
            # Append the footnote to the tree
            # footnotes.append(deepcopy(footnote))

            # Ensure that all text trailing the footnote element is preserved
            parent = footnote.getparent()

            parent_text = '' if parent.text is None else parent.text
            footnote_tail = '' if footnote.tail is None else footnote.tail
            parent.text = parent_text + footnote_tail

            # Footnotes are not to be removed, but instead, are to be appended following each line
            # node.append( deepcopy(footnote) )

            # Remove the footnote itself
            footnote.getparent().remove(footnote)

        #  for structural markup for 

        # Handling for typographic feature (e. g. <hi />) and editorial elements (e. g. <gap />)
        # Leave intact; Prefer transformation into HTML5 using XSL Stylesheets

# before
# <hi xmlns="http://www.tei-c.org/ns/1.0" rend="SMALL-CAPS">NCE</hi> on a Time, near 
# <l xmlns="http://www.tei-c.org/ns/1.0" rend="indent(1)" n="3">UNDERLINE_CLASS_OPENChannel-Row_CLASS_CLOSED,<hi rend="SMALL-CAPS">NCE</hi> on a Time, near </l>
# after
# <l xmlns="http://www.tei-c.org/ns/1.0" rend="indent(1)" n="3">SMALL-CAPS_CLASS_OPENNCE_CLASS_CLOSED on a Time, near <hi rend="SMALL-CAPS">NCE</hi> on a Time, near </l>

#                    parent_markup = re.sub('<hi xmlns="http://www.tei-c.org/ns/1.0" rend="' + feature_token + '">', feature_token.upper() + u"_CLASS_OPEN", parent_markup)
#                    parent_markup = re.sub('<hi rend="' + feature_token + '">', feature_token.upper() + u"_CLASS_OPEN", parent_markup)
#                    parent_markup = re.sub('</hi>', u"_CLASS_CLOSED", parent_markup)


        for feature in [{'xpath': 'tei:hi[@rend="italic"]', 'text_token': 'italic', 'tag': 'hiitalic'},
                        {'xpath': 'tei:hi[@rend="display-initial"]', 'text_token': 'display-initial', 'tag': 'hidisplay-italic'},
                        {'xpath': 'tei:hi[@rend="underline"]', 'text_token': 'underline', 'tag': 'hiunderline'},

                        # {'xpath': 'tei:hi[@rend="SMALL-CAPS"]', 'text_token': 'small-caps', 'tag': 'hismall-caps'},
                        {'xpath': 'tei:hi[@rend="SMALL-CAPS"]', 'text_token': 'SMALL-CAPS', 'tag': 'hismall-caps'},

                        {'xpath': 'tei:hi[@rend="sup"]', 'text_token': 'superscript', 'tag': 'hisuperscript'},
                        {'xpath': 'tei:hi[@rend="black-letter"]', 'text_token': 'black-letter', 'tag': 'hiblack-letter'},
                        {'xpath': 'tei:gap', 'text_token': 'gap', 'tag': 'gap'},
                        
                        {'xpath': 'tei:note[@rend="small type flush left"]', 'text_token': 'stanza', 'tag': 'stanza'}, # Handling for stanza heading indices
                        ]:

            feature_xpath = feature['xpath']
            feature_token = feature['text_token']
            feature_tag = feature['tag']

            feature_elements = node.xpath(feature_xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            # feature_elements = [ feature_elements[0] ] if len(feature_elements) > 0 else []

            for feature_element in feature_elements:

                # Resolving SPP-178
                # Ensure that the children are parsed only once
                # However, all feature elements must still be removed

                # Ensure that all text trailing the feature_element element is preserved
                parent = feature_element.getparent()

                parent_tail = parent.tail if parent.tail is not None else ''

                # Currently leads to issues relating to the parsing of redundant, trailing tokens
                # @todo Resolve SPP-178

#                parent_text_head = unicode(parent.text) if parent.text is not None else ''
#                parent_text = parent_text_head + string.join(map( Tokenizer.parse_child, list(parent.iterchildren())), '') + parent_tail
#                parent.text = parent_text

                feature_element.getparent().remove(feature_element)

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

    # Generates a stemmatic tree consisting of many witness TEI Documents in relation to a single base Document    
    @staticmethod
    def stemma(root_witness, witnesses): # Root text of the stemma

        diff_tree = nx.Graph()

        roots = [ root_witness ] * len(witnesses)
        for text_u, text_v in zip(roots, witnesses):

            node_u = text_u['node']
            text_u_id = text_u['id']
            node_v = text_v['node']
            text_v_id = text_v['id']

            diff_u_v_tree = Tokenizer.diff(node_u, text_u_id, node_v, text_v_id)

            diff_tree = nx.compose(diff_tree, diff_u_v_tree)

        # Merging the bases manually is necessary (given that each TextToken Object is a unique key for the graph structure
        # @todo Investigate cases in which TextToken Objects can be reduced simply to string Objects
        # (Unfortunately, the problem still exists in which identical string content between lines can lead to collisions within the graph structure)
        edges = diff_tree.edges()
        filtered_edges = []
        filtered_diff_tree = nx.Graph()

        base_line_edges = []

        for edge in edges:

            u = edge[0] if isinstance(edge[0], TextToken) else edge[-1]

            filtered_edge = []

            for edge_item in diff_tree[u].items(): # For each edge between the line expression u and the related TextNodes...

                line_text = edge_item[0] if type(edge_item[0]) == str else edge_item[-1]
                line_attributes = edge_item[-1] if type(edge_item[-1]) == dict else edge_item[0]

                if(line_attributes['witness'] == 'base'): # Ensure that lines are index uniquely

                    if not unicode(u) in base_line_edges:

                        base_line_edges.append(unicode(u))
                        filtered_diff_tree.add_edge(u, line_text, line_attributes)
                else:

                    # filtered_edge.append(edge_item)
                    filtered_diff_tree.add_edge(u, line_text, line_attributes)

        return filtered_diff_tree

    @staticmethod
    def clean_tokens(tokens):

        output = []
        
        i=0
        j=0
        while i < len(tokens) - 1:

            u = tokens[i]
            v = tokens[i+1]

            # Ensure that initial quotation marks are joined with proceeding tokens
            if u in string.punctuation or u[0] in string.punctuation:

                if len(output) == 0:

                    output.append(u + v)
                else:

                    output = output + [ u + v ]
                i+=1
            else:

                output.append(u)

            if v in string.punctuation or v[0] in string.punctuation:

                output = output + [ u + v ]
                i+=1

            i+=1

        return output

    # Generates a tree structuring the differences identified within two given TEI Documents
    @staticmethod
    def diff(node_u, text_u_id, node_v, text_v_id):

        # print "Comparing {0} to {1}".format(text_u_id, text_v_id)

        # Each node serves as a <tei:text> element for the text being compared
        tree_u = Tokenizer.text_tree(node_u, text_u_id)
        text_u_id = tree_u.name if text_u_id is None else text_u_id

        tree_v = Tokenizer.text_tree(node_v, text_v_id)
        text_v_id = tree_v.name if text_v_id is None else text_v_id

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
                raise Exception("Structural comparison is not yet supported")
            else:
                
                text_node_u = string.join(text_nodes)
                elem_node_u = v if u == text_node_u else u
                nodes_u_dist = data['distance']

                # If there is no matching line within the stanza being compared, simply avoid the comparison altogether
                # @todo Implement handling for addressing structural realignment between stanzas (this would likely lie within Tokenizer.parse_text)
                if not elem_node_u in tree_v:

                    # Try to structurally align the lines by one stanza
                    stanza_node_u_m = re.search('<lg n="(\d+)(?:\-footnotes)"/l n="(\d+)"', elem_node_u)
                    if stanza_node_u_m:

                        stanza_index = int(stanza_node_u_m.group(1))

                        line_index = int(stanza_node_u_m.group(2))

                        elem_node_u_incr = re.sub('lg n="(\d+)"', 'lg n="' + str(stanza_index + 1) + '"', elem_node_u)
                        elem_node_u_decr = re.sub('lg n="(\d+)"', 'lg n="' + str(stanza_index - 1) + '"', elem_node_u)

                        if elem_node_u_incr in tree_v:

                            elem_node_v = tree_v[elem_node_u_incr]

                        elif stanza_index > 0 and elem_node_u_decr in tree_v:

                            elem_node_v = tree_v[elem_node_u_decr]
                        else:

                            continue

                    else:
                        
                        # raise Exception("Failed to parse the XML for the following: " + elem_node_u)
                        continue

                else:

                    elem_node_v = tree_v[elem_node_u]
                    
                text_nodes_v = elem_node_v.keys()
                
                text_node_v = string.join(text_nodes_v)

                # If the text node has not been linked to the <l> node, attempt to match using normalization

#                nodes_v_dist = 0
#                if not text_node_v in elem_node_v:

#                    text_node_v = text_node_v.strip()
#                    text_node_v_norm = re.sub(r'\s+', '', text_node_v)

#                    for text_node_u in elem_node_v.keys():

#                        text_node_u_norm = re.sub(r'\s+', '', text_node_u)
#                        if text_node_v_norm == text_node_u_norm:

#                            nodes_v_dist = elem_node_v[text_node_u]['distance']

#                    if not text_node_v in elem_node_v:

#                        nodes_v_dist = 0
#                    if nodes_v_dist is None:

#                        raise Exception('Could not match the variant text string :"' + text_node_v + '" to those in the base: ' + string.join(elem_node_v.keys()) )
#                else:

                if not text_node_v in elem_node_v:

                    nodes_v_dist = 0
                else:

                    nodes_v_dist = elem_node_v[text_node_v]['distance']

                # Just add the edit distance
                edit_dist = nodes_u_dist + nodes_v_dist + nltk.metrics.distance.edit_distance(text_node_u, text_node_v)

                # Note: This superimposes the TEI structure of the base text upon all witnesses classified as variants
                # Add an edge between the base element and the base text
                diff_tree.add_edge(elem_node_u, TextToken(text_node_u), distance=0, witness=text_u_id, feature='line')

                # Add an additional edge between the base element and the base text
                diff_tree.add_edge(elem_node_u, TextToken(text_node_v), distance=edit_dist, witness=text_v_id, feature='line')

                # Now, add the tokenized texts
                # Default to the Treebank tokenizer
                # text_tokenizer = TreebankWordTokenizer()
                text_tokenizer = PunktWordTokenizer()

#                text_tokens_u = text_tokenizer.tokenize(text_node_u)
#                text_tokens_u = Tokenizer.clean_tokens(text_tokens_u)

#                text_tokens_v = text_tokenizer.tokenize(text_node_v)
#                text_tokens_v = Tokenizer.clean_tokens(text_tokens_v)
                raw_text_tokens_u = text_node_u.split()
                raw_text_tokens_v = text_node_v.split()

                # Clean the tokens for cases of imbalanced markup
                # This handles cases in which opening and closing tags have separate tokens between the tags
                #
                text_token_index = 0
                text_tokens = [ [],
                                [] ]

                for text_tokens_set in [raw_text_tokens_u, raw_text_tokens_v]:

                    for raw_text_token in text_tokens_set:

                        text_token = raw_text_token

                        markup_init_match = re.findall(r'([A-Z]+?)_CLASS_CLOSED', raw_text_token)
                        markup_term_match = re.findall(r'([A-Z]+?)_CLASS_OPEN', raw_text_token)

                        if len(markup_init_match) > len(markup_term_match):

                            text_token = markup_init_match[-1] + '_CLASS_OPEN' + text_token
                        elif len(markup_init_match) < len(markup_term_match):

                            text_token += markup_term_match[-1] + '_CLASS_CLOSED'

                        text_tokens[text_token_index].append(text_token)

                    text_token_index += 1

                text_tokens_v, text_tokens_u = text_tokens.pop(), text_tokens.pop()

                # Debugging

                # Attempt to align the sequences (by adding gaps where necessary)
                # THIS HAS BEEN TEMPORARILY DISABLED
                # Strip all tags and transform into the lower case
                # Here is where the edit distance is to be inserted
                text_tokens_u_len = len(text_tokens_u)
                text_tokens_v_len = len(text_tokens_v)

                # if text_tokens_u_len != text_tokens_v_len and min(text_tokens_u_len, text_tokens_v_len) > 0:
                if False:

                    for i, diff in enumerate(ndiff(text_tokens_u, text_tokens_v)):

                        opcode = diff[0:1]
                        if opcode == '+':

                            text_tokens_u = text_tokens_u[0:i] + [''] + text_tokens_u[i:]
                            # pass

                        elif opcode == '-':

                            text_tokens_v = text_tokens_v[0:i] + [''] + text_tokens_v[i:]
                            # pass

                text_tokens_intersect = [ (i,e) for (i,e) in enumerate(text_tokens_u) if i < len(text_tokens_v) and text_tokens_v[i] == e ]

                # max_text_tokens = max(len(text_tokens_u), len(text_tokens_v))
                # text_tokens_intersect = [''] * max_text_tokens
                # text_tokens_diff_u = [''] * max_text_tokens

                # text_tokens_diff_u = filter(lambda t: not t in text_tokens_v, text_tokens_u)
                # text_tokens_diff_u = [ (i,e) for (i,e) in enumerate(text_tokens_u) if i < len(text_tokens_v) and text_tokens_v[i] != e ]
                text_tokens_diff_u = [ (i,e) for (i,e) in enumerate(text_tokens_u) if i < len(text_tokens_v) ]
                
                # text_tokens_diff_v = [t for t in text_tokens_v if not t in text_tokens_u]
                # text_tokens_diff_v = [ (i,e) for (i,e) in enumerate(text_tokens_v) if i < len(text_tokens_u) and text_tokens_u[i] != e ]
                text_tokens_diff_v = [ (i,e) for (i,e) in enumerate(text_tokens_v) if i < len(text_tokens_u) ]

                # Edges override the different tokens
                # "line of tokens"
                # |    \  \
                # line of tokens

                # For tokens in both sets
                for pos,text_token in text_tokens_intersect:

                    # pos = text_tokens_u.index(text_token)
                    # diff_tree.add_edge(elem_node_u, text_token, distance=0, witness='base', feature='ngram', position=pos)

                    token = TextToken(text_token)
                    # diff_tree.add_edge(elem_node_u, token, distance=0, witness='common', feature='ngram', position=pos)

                # @todo Refactor
                for pos,text_token in text_tokens_diff_u:

                    # pos = text_tokens_u.index(text_token)
                    # diff_tree.add_edge(elem_node_u, '_' + text_token, distance=0, witness=text_u_id, feature='ngram', position=pos)

                    token = TextToken(text_token)
                    diff_tree.add_edge(elem_node_u, token, distance=0, witness=text_u_id, feature='ngram', position=pos)

                # @todo Refactor
                for pos,text_token in text_tokens_diff_v:

                    # Disjoint
                    # pos = text_tokens_v.index(text_token)
                    # diff_tree.add_edge(elem_node_u, '__' + text_token, distance=None, witness=text_v_id, feature='ngram', position=pos)

                    token = TextToken(text_token)
#                    diff_tree.add_edge(elem_node_u, token, distance=None, witness=text_v_id, feature='ngram', position=pos)
                    diff_tree.add_edge(elem_node_u, token, distance=nltk.metrics.distance.edit_distance(text_tokens_u[pos], token.value), witness=text_v_id, feature='ngram', position=pos)
                    
            pass

        return diff_tree
