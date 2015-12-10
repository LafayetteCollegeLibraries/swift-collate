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

# @todo Refactor into a separate Module
class TextEntity(object):

    def __init__(self):

        self.lines = []

class Titles(TextEntity):

    pass

class Headnotes(TextEntity):

    pass

class Body(TextEntity):

    pass

class Footnotes(TextEntity):

    pass

class Token(object):

    def __init__(self, value, index, classes=[], markup={}):

        self.value = value
        self.index = index
        self.classes = classes
        self.markup = markup

class DifferenceToken(Token):

    def __init__(self, base_token, other_token):

        self.distance = self.find_distance(base_token, other_token)

        super(DifferenceToken, self).__init__(other_token.value, other_token.index, other_token.classes, other_token.markup)

    def find_distance(self, base_token, other_token):

        distance = nltk.metrics.distance.edit_distance(base_token.value, other_token.value)

        return distance

class SwiftSentenceTokenizer(object):
    """The sentence tokenizer specialized for the Swift Poems Project
    
    """

    def tokenize(self, value):

        # For handling cases related to non-breaking spaces inserted within strings (e. g. "I 'd")
        # Please see SPP-269
        value = re.sub(r"(.)[\s ]('.)", "\\1\\2", value)

        tokens = value.split()

        return tokens

class SwiftCleanSentenceTokenizer(SwiftSentenceTokenizer):

    def tokenize(self, value):

        # Handling for \\ tokens
        value = re.sub(r"\\(.+?)\\", "", value)

        super(SwiftCleanSentenceTokenizer, self).tokenize(value)

class Line(object):

    def __init__(self, value, index, tokenizer=SwiftSentenceTokenizer, classes={}, markup={}):

        self.value = value
        self.index = index
        self.tokens = []
        self.tokenizer = tokenizer()
        self.classes = classes
        self.markup = markup

    def __unicode__(self):

        return unicode(self.value).encode('utf-8')

    def __str__(self):

        return self.__unicode__()

    def tokenize(self):

        token_values = self.tokenizer.tokenize(self.value)
        
        line_value = self.value

        # Need to parse the classes
        for token_index, token_value in enumerate(token_values):

            # Filter for the classes
            _classes = filter(lambda _class: _class['start'] >= string.find(line_value, token_value) and _class['end'] <= string.find(self.value, token_value) + len(token_value), self.classes.itervalues())
            token_classes = map(lambda _class_key: _class_key, self.classes.iterkeys())

            # Filter for the markup
            token_markup = {}
            _markup = {}

            for tag_name, tag_list in self.markup.iteritems():

                for tag_items in tag_list:

                    markup_items = tag_items['markup']
                    range_items = tag_items['range']

#                    if range_items['start'] == string.find(line_value, token_value) and range_items['end'] <= string.find(line_value, token_value) + len(token_value) - 1:
                    if range_items['start'] == string.find(line_value, token_value):

                        _markup = token_markup.copy()
                        _markup.update(markup_items)
                        token_markup = _markup

                        # Replace
                        # line_value = ''.replace(line_value, token_value, '', 1)
            
            # Create the token
            token = Token(token_value, token_index, token_classes, token_markup)

            self.tokens.append(token)

class FootnoteLine(Line):

    def __init__(self, value, index, target_id, distance_from_parent, tokenizer=SwiftSentenceTokenizer, classes={}, markup={}):
        
        self.target_id = target_id
        self.distance_from_parent = distance_from_parent
        super(FootnoteLine, self).__init__(value, index, tokenizer=tokenizer, classes=classes, markup=markup)

class DifferenceLine(Line):

    def __init__(self, base_line, other_line, tokenizer=SwiftSentenceTokenizer):

        self.other_line = other_line
        self.distance = self.find_distance(base_line, other_line)

        self.position = ''

        # super(DifferenceLine, self).__init__(other_line.value, other_line.index, tokenizer=tokenizer, classes=other_line.classes, markup=other_line.markup)
        super(DifferenceLine, self).__init__(base_line.value, base_line.index, tokenizer=tokenizer, classes=base_line.classes, markup=base_line.markup)

    def find_distance(self, base_line, other_line):

        distance = nltk.metrics.distance.edit_distance(base_line.value, other_line.value)

        return distance

    def tokenize(self):

        super(DifferenceLine, self).tokenize()
        self.other_line.tokenize()

        # Debug
#        if self.index == '1' and 'Beef-steaks.' in self.value:

#            print 'TRACE4'
#            print map(lambda t: t.value, self.tokens)
#            print 'TRACE5'
#            print map(lambda t: t.value, self.other_line.tokens)

        diff_tokens = []

        # An alignment must be performed in order to ensure that the tokens for each line are parsed
        base_tokens = self.tokens
        other_tokens = self.other_line.tokens

        if len(base_tokens) > other_tokens:

            # Search for the terms
            for i, other_token in enumerate(other_tokens):

                # Attempt to find the token
#                index = string.find(self.value, other_token)
#                if index > -1:

#                    pass
                
                pass
            
            pass
        elif len(base_tokens) < other_tokens:

            # 
            pass

        for base_token, other_token in zip(base_tokens, other_tokens):
            
            diff_tokens.append(DifferenceToken(base_token, other_token))
#            print "trace" + str(diff_tokens[-1].distance)

        self.tokens = diff_tokens

class DifferenceSet(object):

    def __init__(self):

        self.lines = {}

    def lines(self, line_id):

        if not line_id in self.lines:

            self.lines[line_id] = DifferenceLine()

        return self.lines[line_id]

class DifferenceText(object):

    def __init__(self, base_text, other_text):

        self.other_text = other_text

        self.titles = DifferenceSet()
        self.headnotes = DifferenceSet()
        self.body = DifferenceSet()
        self.footnotes = DifferenceSet()

        # This retrieves the titles from the text
        for title_line_index, title_line in enumerate(base_text.titles.lines):

            # Retrieve the line from the base text
            this_title_line = base_text.titles.lines[title_line_index]

            # Work-arounds for the sorting of lines by index
            try:

                other_title_line = other_text.titles.lines[title_line_index]

                diff_line = DifferenceLine(this_title_line, other_title_line)
                
                diff_line.tokenize()

                # Construct the key from the index of the footnote concatenated to the ID for the line, concatenated to the character distance
                # footnote_key = str(footnote_line_index + 1) + this_footnote_line.target_id + '#' + str(this_footnote_line.distance_from_parent)

                self.titles.lines[title_line_index] = diff_line
            except:

                pass

        # This retrieves the headnotes from the text
        for headnote_line_index, headnote_line in enumerate(base_text.headnotes.lines):

            this_headnote_line = base_text.headnotes.lines[headnote_line_index]

            print this_headnote_line
            print 'trace'

        # This retrieves the footnotes from the text
        for footnote_line_index, footnote_line in enumerate(base_text.footnotes.lines):

            # Retrieve the line from the base text
            this_footnote_line = base_text.footnotes.lines[footnote_line_index]

            # Work-arounds for the sorting of lines by index
            try:

                other_footnote_line = other_text.footnotes.lines[footnote_line_index]

                diff_line = DifferenceLine(this_footnote_line, other_footnote_line)
                
                diff_line.tokenize()

                # Construct the key from the index of the footnote concatenated to the ID for the line, concatenated to the character distance
                footnote_key = str(footnote_line_index + 1) + this_footnote_line.target_id + '#' + str(this_footnote_line.distance_from_parent)

                self.footnotes.lines[footnote_key] = diff_line
            except:

                pass

        # This retrieves the lines from the body
        for line_index, line in enumerate(base_text.body.lines):

            # Retrieve the line from the base text
            this_line = base_text.body.lines[line_index]

            # Work-arounds for the sorting of lines by index
            # if line_index == 0: continue

            try:

                other_line = other_text.body.lines[line_index]

                diff_line = DifferenceLine(this_line, other_line)
                diff_line.tokenize()

                self.body.lines[line_index] = diff_line
            except:

                pass

    def __unicode__(self):

        pass

class Text(object):

    EMPHATIC_MARKUP_TAGS = ['hi']
    EMPHATIC_MARKUP = {
        'SUP': { 'sup': {} },
        'UNDERLINE': { 'u': {} }
        }

    EDITORIAL_MARKUP_TAGS = ['unclear', 'add', 'del', 'subst', 'sic', 'gap']
    EDITORIAL_MARKUP = {

        'unclear': {
            'a': {
                'data-toggle': 'popover',
                }
            },
        'add': {
            'a': {
                'data-toggle': 'popover',
                }
            },
        'del': {
            'a': {
                'data-toggle': 'popover',
                }
            },
        'subst': {
            'a': {
                'data-toggle': 'popover',
                'href': '#',
                }
            },
        'sic': {
            'a': {
                'data-toggle': 'popover',
                }
            },
        'gap': {
            'a': {
                'data-toggle': 'popover',
                }
            },
        }

    def __init__(self, doc, doc_id, tokenizer=SwiftSentenceTokenizer):

        self.titles = Titles()
        self.headnotes = Headnotes()
        self.body = Body()
        self.footnotes = Footnotes()

        self.doc = doc
        self.id = doc_id
        self.tokenizer = tokenizer

        self.markup_starts = None

        # Python work-around
        self.last_child_values = []
        self.last_data_content_value = ''
        self.new_data_content_value = ''

        self.tokenize()

    def parse_element(self, element):

        result = {}
        result_text = ''
        _result_classes = {}
        _result_markup = {}

        element_text = '' if element.text is None else element.text
        element_tail = '' if element.tail is None else element.tail

        element_tag_name = element.xpath('local-name()')

        # Work-around
        # @todo Refactor

        # Store where the class begins and ends
        parent = element.getparent()

#        if self.markup_starts is None:

#            self.markup_starts = 0 if parent.text is None else len(parent.text)

        # Specialized handling for editorial markup
        if element_tag_name in self.EDITORIAL_MARKUP_TAGS:

            # Index the markup
            markup_key = element_tag_name
            
            markup_values = self.EDITORIAL_MARKUP[markup_key]

            if element_tag_name == 'subst':

                # Grab the first child
                subst_children = list(element)
                data_content = '' if subst_children[0].text is None else subst_children[0].text

                # Increment the markup ending
                markup_ends = self.markup_starts + len(element_tail.split(' ')[0])

                # Ensure that any additional strings (following the marked up token) increase the markup
#                if len( element_tail.split(' ') ) > 1:

#                    self.markup_starts += 1

                for subst_child in subst_children:

                    subst_child.getparent().remove(subst_child)

            else:

                markup_ends = self.markup_starts + len(element_text)
                data_content = element_text

            # For the popover
            markup_values['a']['data-content'] = data_content

            _result_markup[markup_key] = [{
                    
                'markup' : markup_values,
                'range' : {'start':self.markup_starts, 'end':markup_ends}
                }]

            self.markup_starts = markup_ends + 1

            element.getparent().remove(element)

        # Specialized handling for <hi> nodes
        # Capitalized style values are used as keywords
        # @todo Refactor for an encoded approach
        elif element_tag_name in self.EMPHATIC_MARKUP_TAGS:

            # Index the class
            emphatic_rend_value = element.get('rend').upper()

            # Store where the class begins and ends
#            parent = element.getparent()
#            class_starts = 0 if parent.text is None else len(parent.text)            
#            class_ends = class_starts + len(element_text)
            class_ends = self.markup_starts + len(element_text)

            # If this is markup, encode the token
            if emphatic_rend_value in self.EMPHATIC_MARKUP:

                # _result_markup[self.EMPHATIC_MARKUP[emphatic_rend_value]] = {'start':class_starts, 'end':class_ends}
                _result_markup[emphatic_rend_value] = [{
                    
                    'markup' : self.EMPHATIC_MARKUP[emphatic_rend_value],
                    'range' : {'start':self.markup_starts, 'end':class_ends}
                    }]
            else:

                _result_classes[emphatic_rend_value] = {'start':self.markup_starts, 'end':class_ends}

            self.markup_starts = class_ends + 1
            element.getparent().remove(element)

        elif self.markup_starts is None:

            self.markup_starts = 0 if element_text is None else len(element_text)
        else:

            # self.markup_starts += 0 if parent.text is None else len(parent.text)
            self.markup_starts += 0 if element_text is None else len(element_text)

        children_text = ''
        children_markup = {}
        children_classes = {}

        if len(element):

            for child_element in list(element):

                children_values = self.parse_element(child_element)
                children_text += children_values['text']

                # Merge the markup parsed from the children
                _children_markup = children_markup

#                _children_markup.update(children_values['markup'])
                for children_markup_key, children_markup_values in children_values['markup'].iteritems():

                    if children_markup_key in _children_markup:

                        if children_markup_key == 'subst':
                            
                            self.new_data_content_value = children_markup_values[0]['markup'].values()[-1]['data-content']
                            _children_markup[children_markup_key][-1]['markup']['a']['data-content'] = self.last_data_content_value

                        _children_markup[children_markup_key].extend( children_markup_values )

                        if children_markup_key == 'subst':

                            last_values = _children_markup[children_markup_key][-1].copy()
                            last_values['markup']['a']['data-content'] = self.new_data_content_value

                            _children_markup[children_markup_key][-1]['markup']['a']['data-content'] = self.new_data_content_value
                            _children_markup[children_markup_key][0]['markup']['a']['data-content'] = self.last_data_content_value

                            first_values = _children_markup[children_markup_key][0].copy()
                            first_values['markup']['a']['data-content'] = self.last_data_content_value

                            # _children_markup[children_markup_key][0] = first_values
                            # _children_markup[children_markup_key][-1] = last_values
                            _children_markup[children_markup_key] = None
                            # _children_markup[children_markup_key] = [first_values, last_values]
                            _children_markup[children_markup_key] = [{'markup': {'a': {'data-toggle': 'popover', 'href': '#', 'data-content': self.last_data_content_value }}, 'range': first_values['range']}, {'markup': {'a': {'data-toggle': 'popover', 'href': '#', 'data-content': self.new_data_content_value }}, 'range': last_values['range']}]

                    elif children_markup_key not in _children_markup:

                        _children_markup[children_markup_key] = children_markup_values

                        # Work-around
                        self.last_child_values = children_markup_values

                        if children_markup_key == 'subst':

                            self.last_data_content_value = children_markup_values[0]['markup'].values()[-1]['data-content']

                children_markup = _children_markup


        result_text = element_text + children_text + element_tail

        # Structure the markup for the line
        result_markup = _result_markup.copy()
#        result_markup.update(children_markup)

        for children_markup_key, children_markup_values in children_markup.iteritems():

            if children_markup_key in result_markup:

                result_markup[children_markup_key].extend( children_markup_values )
            elif children_markup_key not in result_markup:

                result_markup[children_markup_key] = children_markup_values

        # Structure the classes for the line
        result_classes = _result_classes.copy()
        result_classes.update(children_classes)

        result['text'] = result_text

        result['markup'] = result_markup
        result['classes'] = result_classes

        return result

    def tokenize_titles(self, line_xpath = '//tei:title', line_namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}):

        unsorted_lines = {}

        elements = self.doc.xpath(line_xpath, namespaces=line_namespaces)
        for element in elements:

            self.markup_starts = None

            line_values = self.parse_element(element)

            line_value = line_values['text']
            line_markup = line_values['markup']
            line_classes = line_values['classes']
            line_index = element.get('n')

            line = Line(line_value, line_index, tokenizer=self.tokenizer, classes=line_classes, markup=line_markup)

            self.titles.lines.append( line )

    def tokenize_body(self, line_xpath = '//tei:body/tei:div[@type="book"]/tei:div/tei:lg[@type="stanza"]/tei:l[@n]', line_namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}):

        unsorted_lines = {}

        elements = self.doc.xpath(line_xpath, namespaces=line_namespaces)
        for element in elements:

            self.markup_starts = None

            line_values = self.parse_element(element)

            line_value = line_values['text']
            line_markup = line_values['markup']
            line_classes = line_values['classes']
            line_index = element.get('n')

            line = Line(line_value, line_index, tokenizer=self.tokenizer, classes=line_classes, markup=line_markup)

            self.body.lines.append( line )

#    def tokenize_footnotes(self, line_xpath = '//tei:body/tei:div[@type="book"]/tei:div//tei:note[@place="foot"]', line_namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}):
    def tokenize_footnotes(self, line_xpath = '//tei:note[@place="foot"]', line_namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

        unsorted_lines = {}

        # @todo Refactor
        elements = self.doc.xpath(line_xpath, namespaces=line_namespaces)
        for element in elements:

            self.markup_starts = None

            # Retrieve the target for the footnote using the neighboring <ref>
            # Prune this element (as it contains the footnote number)
            ref_elements = element.xpath('../tei:ref', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            if ref_elements:

                ref_elements[0].getparent().remove(ref_elements[0])

            line_values = self.parse_element(element)
            line_value = line_values['text']
            line_markup = line_values['markup']
            line_classes = line_values['classes']
            line_index = element.get('n')

            # Retrieve the XML ID
            footnote_id = element.get('{%s}id' % 'http://www.w3.org/XML/1998/namespace')

            # Retrieve the target for the footnote using the neighboring <ref>
            # ref_element = element.getprevious()
            # target_id = ref_element.get('target')

            # Retrieve the link group entry for the link

            link_elements = self.doc.xpath('//tei:linkGrp/tei:link[starts-with(@target, "#' + footnote_id + '")]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

            link_element = link_elements[0]
            link_target = link_element.get('target')
            target_id = link_target.split(' ')[-1]

            # Retrieve the distance from the parent
            if element.getparent().text is None:

                distance_from_parent = 0
            else:
                
                distance_from_parent = len(element.getparent().text)

            line = FootnoteLine(line_value, line_index, target_id, distance_from_parent, tokenizer=self.tokenizer, classes=line_classes, markup=line_markup)

            self.footnotes.lines.append( line )

            element.getparent().remove(element)

    def tokenize(self):

        self.tokenize_titles()
#        self.tokenize_headnotes()
        self.tokenize_footnotes()
        self.tokenize_body()

class CollatedTexts:

    def __init__(self):

        self.lines = {}
        pass

    def line(self, line_id):

        if not line_id in self.lines:

            self.lines[line_id] = {'line': None}

        return self.lines[line_id]

class CollatedLines:

    def __init__(self):

        self.witnesses = []

        # dicts cannot be ordered
        self._witness_index = {}

    def witness_index(self, witness_id):

        if not witness_id in self._witness_index:
            index = len(self._witness_index.keys())
            self._witness_index[witness_id] = index

            # Work-around
            self.witnesses.append(None)
        else:
            index = self._witness_index[witness_id]

        return index

    def witness(self, witness_id):

        # Retrieve the index for the witness id
        self.witnesses[self.witness_index(witness_id)] = {'line': None, 'id': witness_id, 'position': None} 

        return self.witnesses[self.witness_index(witness_id)]

class Collation:

    def __init__(self, base_text, diffs):

        self.titles = {}
        self.headnotes = {}
        self.body = {}
        self.footnotes = []
        self.witnesses = []

        # dicts cannot be ordered
        self._witness_index = {}
        self._footnote_index = {}

        for diff in diffs:

            # print diff.__class__

            # Structure the difference set for titles
            for title_line_key, diff_line in diff.titles.lines.iteritems():

                title_line_index = title_line_key

                self.title_line(title_line_index).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(title_line_index)['line'] = diff_line

            # Structure the difference set for headnotes

            # Structure the difference set for footnotes
            for line_key, diff_line in diff.footnotes.lines.iteritems():

                index, target, distance = line_key.split('#')
                target_segments = target.split('-')

                target_index = target_segments[-1]

                # Retrieve the type of structure
                target_structure = target_segments[-2]

                footnote_line_index = index + ' (' + distance + ' characters into ' + target_structure + ' ' + target_index + ')'

                diff_line.position = distance + ' characters into ' + target_structure + ' ' + target_index

                # Collated footnote line tokens
                #
                # CollatedLines
                self.footnote_line(footnote_line_index).witness(diff.other_text.id)['line'] = diff_line

                # Collated footnote lines
                #
                # CollatedTexts
                self.witness(diff.other_text.id).line(footnote_line_index)['line'] = diff_line

            # Structure the difference set for indexed lines
            for line_id, diff_line in diff.body.lines.iteritems():

                self.body_line(line_id).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(line_id)['line'] = diff_line

    # Retrieve the footnote index
    def footnote_index(self, footnote_id):
        """Retrieves an index for the ordering of footnotes
    
        :param footnote_id: The key for the footnote
        :type footnote_id: str.
        :returns:  int -- the index for the list of sorted collated footnotes

        """

        if not footnote_id in self._footnote_index:
            index = len(self._footnote_index.keys())
            self._footnote_index[footnote_id] = index

            # Work-around
            self.footnotes.append(None)
        else:
            index = self._footnote_index[footnote_id]

        return index

    def footnote_line(self, line_id):
        """Sets and retrieves the set of collated lines for a footnote in the base text
    
        :param line_id: The key for the footnote
        :type line_id: str.
        :returns:  CollatedLines -- the set of collated lines for the footnotes.

        """

        # Retrieve the index for the footnote id
        index = self.footnote_index(line_id)

        if index >= len(self.footnotes) - 1:
            self.footnotes[index] = CollatedLines()

        return self.footnotes[index]

    def title_line(self, line_id):

        if not line_id in self.titles:

            self.titles[line_id] = CollatedLines()

        return self.titles[line_id]

    def body_line(self, line_id):

        if not line_id in self.body:

            self.body[line_id] = CollatedLines()

        return self.body[line_id]

    def witness_index(self, witness_id):

        if not witness_id in self._witness_index:
            index = len(self._witness_index.keys())
            self._witness_index[witness_id] = index

            # Work-around
            self.witnesses.append(None)
        else:
            index = self._witness_index[witness_id]

        return index

    def witness(self, witness_id):

        # Retrieve the index for the witness id
        self.witnesses[self.witness_index(witness_id)] = CollatedTexts()

        return self.witnesses[self.witness_index(witness_id)]

# Deprecated

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
    def parse_text(resource):

        response = urllib.urlopen(resource)
        data = response.read()

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

                # Deprecated

#                print "after"
#                print "\n"
#                print [ (i,e) for (i,e) in enumerate(text_tokens_u) ]
#                print "\n"
#                print [ (i,e) for (i,e) in enumerate(text_tokens_v) ]
                # print enumerate(text_tokens_v)
                                    
                # text_tokens_intersect = filter(lambda t: t in text_tokens_v, text_tokens_u)
                text_tokens_intersect = [ (i,e) for (i,e) in enumerate(text_tokens_u) if i < len(text_tokens_v) and text_tokens_v[i] == e ]

                # max_text_tokens = max(len(text_tokens_u), len(text_tokens_v))
                # text_tokens_intersect = [''] * max_text_tokens
                # text_tokens_diff_u = [''] * max_text_tokens

                # text_tokens_diff_u = filter(lambda t: not t in text_tokens_v, text_tokens_u)
                # text_tokens_diff_u = [ (i,e) for (i,e) in enumerate(text_tokens_u) if i < len(text_tokens_v) and text_tokens_v[i] != e ]
                text_tokens_diff_u = [ (i,e) for (i,e) in enumerate(text_tokens_u) if i < len(text_tokens_v) ]
                
#                print 'tokens in u'
#                print text_tokens_u
#                print 'tokens in v'
#                print text_tokens_v

#                print elem_node_u
#                print 'tokens in u and v'
#                print text_tokens_intersect
#                print 'tokens in just u'
#                print text_tokens_diff_u

                # text_tokens_diff_v = [t for t in text_tokens_v if not t in text_tokens_u]
                # text_tokens_diff_v = [ (i,e) for (i,e) in enumerate(text_tokens_v) if i < len(text_tokens_u) and text_tokens_u[i] != e ]
                text_tokens_diff_v = [ (i,e) for (i,e) in enumerate(text_tokens_v) if i < len(text_tokens_u) ]

#                print 'tokens in just v'
#                print text_tokens_diff_v

                # Edges override the different tokens
                # "line of tokens"
                # |    \  \
                # line of tokens

#                print 'trace5: tokens for ' + elem_node_u
#                print diff_tree[elem_node_u]

                # For tokens in both sets
                for pos,text_token in text_tokens_intersect:

                    # pos = text_tokens_u.index(text_token)
                    # diff_tree.add_edge(elem_node_u, text_token, distance=0, witness='base', feature='ngram', position=pos)

#                    print 'Adding the token "' + text_token + '" for the line ' + elem_node_u + 'at the position ' + str(pos) + ' for the witness common'

                    token = TextToken(text_token)
                    # diff_tree.add_edge(elem_node_u, token, distance=0, witness='common', feature='ngram', position=pos)

#                print 'trace4: tokens for ' + elem_node_u
#                print diff_tree[elem_node_u]

                # @todo Refactor
                for pos,text_token in text_tokens_diff_u:

                    # pos = text_tokens_u.index(text_token)
                    # diff_tree.add_edge(elem_node_u, '_' + text_token, distance=0, witness=text_u_id, feature='ngram', position=pos)

#                    print 'Adding the token "' + text_token + '" for the line ' + elem_node_u + 'at the position ' + str(pos) + ' for the witness ' + text_u_id

                    token = TextToken(text_token)
                    diff_tree.add_edge(elem_node_u, token, distance=0, witness=text_u_id, feature='ngram', position=pos)

                # @todo Refactor
                for pos,text_token in text_tokens_diff_v:

                    # Disjoint
                    # pos = text_tokens_v.index(text_token)
                    # diff_tree.add_edge(elem_node_u, '__' + text_token, distance=None, witness=text_v_id, feature='ngram', position=pos)

#                    print 'Adding the token "' + text_token + '" for the line ' + elem_node_u + 'at the position ' + str(pos) + ' for the witness ' + text_v_id

                    token = TextToken(text_token)
#                    diff_tree.add_edge(elem_node_u, token, distance=None, witness=text_v_id, feature='ngram', position=pos)
                    diff_tree.add_edge(elem_node_u, token, distance=nltk.metrics.distance.edit_distance(text_tokens_u[pos], token.value), witness=text_v_id, feature='ngram', position=pos)
                    
            pass

        return diff_tree
