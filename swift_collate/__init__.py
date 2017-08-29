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

from text import Token

class TextToken:

    def __init__(self, ngram):

        self.value = ngram

    def __str__(self):

        return self.value

    @staticmethod
    def classes(ngram):

        output = ngram
        classes = []

        for element_name, element_classes in { 'indent': ['indent'],
                                               'display-initial': [ 'display-initial' ],
                                               'black-letter': [ 'black-letter' ],
                                               }.iteritems():

            if re.match(element_name.upper() + '_ELEMENT', output) or re.match(element_name.upper() + '_CLASS_OPEN', output):

                classes.extend(element_classes)
        return classes

    # This provides the HTML markup for the intermediary strings used for tokenization
    #
    @staticmethod
    def escape(ngram):

        output = ngram

        for class_name, markup in { 'italic': [ '<i>', '</i>' ],
                                    'display-initial': [ '<span>', '</span>' ],
                                    'underline': [ '<u>', '</u>' ],
                                    'small-caps': [ '<small>', '</small>' ],
                                    'black-letter': [ '<span>', '</span>' ],
                                    }.iteritems():

            class_closed_delim = class_name.upper() + '_CLASS_CLOSED'
            class_opened_delim = class_name.upper() + '_CLASS_OPEN'

            # Anomalous handling for cases in which the display initials are capitalized unnecessarily
            #
            if class_name == 'display-initial':

                #output = re.sub(class_name.upper() + '_CLASS_CLOSED', markup[-1], output)
                #output = re.sub(class_name.upper() + '_CLASS_OPEN', markup[0], output)

                # output = output.lower().capitalize()

                markup_match = re.match( re.compile(class_opened_delim + '(.+?)' + class_closed_delim + '(.+?)\s?'), output )

                if markup_match:

                    markup_content = markup_match.group(1) + markup_match.group(2)

                    output = re.sub( re.compile(class_opened_delim + '(.+?)' + class_closed_delim + '(.+?)\s?'), markup[0] + markup_content.lower().capitalize() + markup[1], output )
            else:

                output = re.sub(class_name.upper() + '_CLASS_CLOSED', markup[-1], output)
                output = re.sub(class_name.upper() + '_CLASS_OPEN', markup[0], output)
                # output = re.sub( re.compile(class_opened_delim + '(.+?)' + class_closed_delim), markup[0] + '\\1' + markup[1], output )

        for element_name, markup in { 'gap': '<br />',
                                      'indent': '<span class="indent">&#x00009;</span>',
                                      }.iteritems():

            output = re.sub(element_name.upper() + '_ELEMENT', markup, output)

        return output

class ElementToken:  

    def __init__(self, name=None, attrib=None, children=None, text=None, doc=None, **kwargs):

        if doc is not None:

            name = doc.xpath('local-name()')
            attrib = doc.attrib
            children = list(doc)
            text = string.join(list(doc.itertext())) if doc.text is not None else ''

            # Work-around
            parents = doc.xpath('..')
            parent = parents.pop()
            
            if parent.get('n') is None:

                parent_name = parent.xpath('local-name()') if name == 'l' else parent.xpath('local-name()')
            else:
                parent_name = parent.xpath('local-name()') + ' n="' + parent.get('n') + '"' if name == 'l' else parent.xpath('local-name()')


        self.name = name
        self.attrib = attrib

        # Generate a string consisting of the element name and concatenated attributes (for comparison using the edit distance)
        # Note: the attributes *must* be order by some arbitrary feature

        # Work-around for the generation of normalized keys (used during the collation process)
        # @todo Refactor

        # Line elements must be uniquely identified using @n values
        # Resolves SPP-229
        if self.name == 'lg':

            # self.value = '<' + parent_name + '/' + self.name
            self.value = '<' + self.name
            attribs = [(k,v) for (k,v) in attrib.iteritems() if k == 'n']
        elif self.name == 'l' or self.name == 'p':

            if 'n' in attrib and re.match('footnotes', attrib['n']):

                self.value = '<' + parent_name + '/' + self.name
            else:

                self.value = '<' + self.name
                
            attribs = [(k,v) for (k,v) in attrib.iteritems() if k == 'n']
        else:

            self.value = '<' + self.name
            # attribs = self.attrib.iteritems()
            attribs = [(k,v) for (k,v) in attrib.iteritems() if k == 'n']

        # Generate the key for the TEI element
        for attrib_name, attrib_value in attribs:

            self.value += ' ' + attrib_name + '="' + attrib_value + '"'
        self.value += ' />'

        self.children = children

        # Parsing for markup should occur here
        if name == 'l' or name == 'p':

            doc_markup = etree.tostring(doc)
            for feature in [{'xml': '<hi rend="italic">', 'text_token': 'italic'},
                            {'xml': '<hi rend="display-initial">', 'text_token': 'display-initial'},
                            {'xml': '<hi rend="underline">', 'text_token': 'underline'},
                            {'xml': '<gap>', 'text_token': 'gap'}]:

                feature_xml = feature['xml']

                doc_markup = re.sub(feature_xml , string.upper(feature['text_token']) + u"_CLASS_OPEN", doc_markup)
            doc_markup = re.sub('</hi>', u"_CLASS_CLOSED", doc_markup)

            new_doc = etree.fromstring(doc_markup)
            text = string.join(list(new_doc.itertext())) if new_doc.text is not None else ''

        # Insert the identation values for the rendering
        if 'rend' in attrib:

            rend = attrib['rend']
            indent_match = re.match(r'indent\((\d)\)', rend)
            if indent_match:

                indent_value = int(indent_match.group(1))
                indent_tokens = [u"INDENT_ELEMENT"] * indent_value
                indent = ''.join(indent_tokens)

                text = indent + text

        self.text = text

class DiffFragmentParser:

    @staticmethod
    def parse(tree):

        pass

# The "Diff Fragment" Entity passed to the Juxta visualization interface

# The following JSON is retrieved from the server
# [{
#     "range": {
#         "start": 19,
#         "end": 29
#     },
#     "witnessName": "welcome2",
#     "typeSymbol": "&#9650;&nbsp;",
#     "fragment": " to Juxta! / <span class='change'>In getting</span> started, you should..."
# }]

class DiffFragment:

    @staticmethod
    def format_fragment(srcFrag, origRange = [], contextRange = [], maxLen=None):

        pass

    def __init__(self, start, end, witness_name, edit_dist, fragment):

        self.range = [start, end]
        self.witness_name = witness_name

        if edit_dist > -1:

            self.type_symbol = "&#9650;&nbsp;"
        elif edit_dist == 0:

            self.type_symbol = "&#10006;&nbsp;";
        else:

            self.type_symbol = "&#10010;&nbsp;"
        
        self.fragment = fragment

class ComparisonSetTei:
    """
    Class for TEI Parallel Segmentation Documents serializing Juxta WS Comparison Sets
    """

    tei_doc = """
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>set_a</title>
                <respStmt>
                    <resp>Conversion from Juxta comparison set to TEI-conformant markup</resp>
                    <name>Generated by the Swift Diff Service for Juxta Commons</name>
                </respStmt>
            </titleStmt>
            <publicationStmt><p/></publicationStmt>
            <sourceDesc><p/></sourceDesc>
        </fileDesc>
        <encodingDesc>
            <variantEncoding location="internal" method="parallel-segmentation"/>
        </encodingDesc>
    </teiHeader>
    
    <text>
        <front>
            <div>
                <listWit>
                    <witness xml:id="wit-1136">source_b</witness>
                    <witness xml:id="wit-1135">source_a</witness>
                </listWit>
            </div>
        </front>
        <body>
            <p>     Songs of Innocence<lb/> # <head>Songs of Innocence</head>
 <lb/>
  Introduction<lb/>
  Piping down the valleys wild, <lb/>
 Piping songs of pleasant glee, <lb/>
 On a cloud I saw a child, <lb/>
 And he laughing said to me: <lb/>
 <lb/>
 <lb/>
 <lb/>
 <lb/>
 <lb/>
 </p>
        </body>
    </text>
</TEI>
"""

    def __init__(self, witnesses):

        self.witnesses = witnesses

        self.doc = etree.parse(self.tei_doc)

        list_wit_elems = self.doc.xpath('tei:text/tei:front/tei:div/tei:listWit')
        self.list_wit = list_wit_elems.pop()

        body_elems = self.doc.xpath('tei:text/tei:body')
        self.body = body_elems.pop()

    def parse(self):

        for witness in self.witnesses:

            self.append_witness(witness)

    def append_witness(self, witness):

        # The ID's are arbitrary, but they must be unique
        # The Witnesses are created anew if they do not exist within the system, and assigned new ID's
        witness_elem = Element('tei:witness', 'xml:id="wit-' + witness.id + '"')
        self.list_wit.append(witness_elem)

        # Update the raw XML for the witness using SQL
        

        # Append elements from the diff tree
        self.body.append()
