
import re
from token import Token
from line import Line, FootnoteLine, LineJSONEncoder
from lxml import etree
import json


class TextEntity(object):

    def __init__(self):
        """Create a text entity which contains multiple instances of SwiftDiff.text.line.Line structuring lines of data

        """

        self.lines = []

class Titles(TextEntity):

    pass

class Headnotes(TextEntity):

    pass

class Body(TextEntity):

    pass

class Footnotes(TextEntity):
    """Footnotes have lines as dicts using the parent line ID's as keys

    """

    def __init__(self):

        self.lines = {}

class Text(object):

    EMPHATIC_MARKUP_TAGS = ['hi']
    EMPHATIC_MARKUP = {
        'SUP': { 'sup': {} },
        'UNDERLINE': { 'u': {} }
        }

    EDITORIAL_MARKUP_TAGS = ['unclear', 'add', 'del', 'subst', 'sic', 'gap']
#    EDITORIAL_MARKUP_TAGS = ['unclear', 'add', 'del', 'subst', 'sic']
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

    def __init__(self, doc, doc_id, tokenizer, tagger = None):

        self.titles = Titles()
        self.title_footnotes = Footnotes()
        self.headnotes = Headnotes()
        self.body = Body()
        self.footnotes = Footnotes()

        if doc is None:
            raise Exception("No XML Document passed for " + doc_id)

        self.doc = doc
        self.id = doc_id
        self.tokenizer = tokenizer
        self.tagger = tagger

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

        # Parsing for line indentation
        if element_tag_name == 'l':

            if element.get('rend'):
                rend_value = element.get('rend').upper()
                index_rend_m = re.match(r'INDENT\((\d)\)', rend_value)

                # If there is an indentation specified for the line element...
                if index_rend_m:
                    index_rend = int(index_rend_m.group(1))
                    index_tokens = ''.join(['|'] * 4)
                    element_text = index_tokens + element_text

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
            if element.get('rend'):
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

        elif element_tag_name == 'ref':

            element_text = ''

            class_ends = self.markup_starts + len(element_text)

#            _result_markup['footnote'] = [{
#                    'markup' : { 'a': { 'class': 'glyphicon glyphicon-hand-down', 'href': '#footnote-' + element_text } },
#                    'range' : { 'start':self.markup_starts, 'end':class_ends }
#                    }]

            self.markup_starts = class_ends + 1

        elif element_tag_name == 'lb':
            # Ensures that line breaks are tokenized as blank spaces (" ")
            # Resolves SPP-609
            # element_text = ' '
            # Resolves SPP-620
            element_text = '_'


            
            
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

        # Handling for <gap> elements
        if element_tag_name == 'gap':
            pass

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
            line_index = element.get('{%s}id' % 'http://www.w3.org/XML/1998/namespace')

            line = Line(line_value, line_index, tokenizer=self.tokenizer, tagger=self.tagger, classes=line_classes, markup=line_markup)

            self.titles.lines.append( line )

    def tokenize_headnotes(self, line_xpath = '//tei:head[@type="note"]', line_namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

        unsorted_lines = {}

        elements = self.doc.xpath(line_xpath, namespaces=line_namespaces)
        for element in elements:

            self.markup_starts = None

            line_values = self.parse_element(element)

            line_value = line_values['text']
            line_markup = line_values['markup']
            line_classes = line_values['classes']
            line_index = element.get('n')

            line = Line(line_value, line_index, tokenizer=self.tokenizer, tagger=self.tagger, classes=line_classes, markup=line_markup)

            self.headnotes.lines.append( line )

    def tokenize_body(self, line_xpath = '//tei:body/tei:div[@type="book"]/tei:div/tei:lg/tei:l[@n]', line_namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}):

        unsorted_lines = {}

        elements = self.doc.xpath(line_xpath, namespaces=line_namespaces)
        for element in elements:

            self.markup_starts = None

            line_values = self.parse_element(element)
            line_value = line_values['text']
            line_markup = line_values['markup']
            line_classes = line_values['classes']
            line_index = element.get('n')

            line = Line(line_value, line_index, tokenizer=self.tokenizer, tagger=self.tagger, classes=line_classes, markup=line_markup)

            self.body.lines.append( line )

    def tokenize_footnotes(self, line_xpath = '//tei:note[@place="foot"]', line_namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):

        unsorted_lines = {}

        # @todo Refactor
        elements = self.doc.xpath(line_xpath, namespaces=line_namespaces)
        for element in elements:

            self.markup_starts = None

            line_values = self.parse_element(element)
            line_value = line_values['text']
            line_markup = line_values['markup']
            line_classes = line_values['classes']
            footnote_index = element.get('n')
            distance_from_parent = 0

            # Retrieve the target for the footnote using the neighboring <ref>
            # ref_element = element.getprevious()
            # target_id = ref_element.get('target')

            # Attempt to extract the ID from the footnote element
            footnote_id = element.get('{%s}id' % 'http://www.w3.org/XML/1998/namespace')

            # If the ID was extracted, attempt to resolve the <ref> link within the <linkGrp>
            if footnote_id is not None:
                link_target = None
                link_elements = self.doc.xpath('//tei:linkGrp/tei:link[starts-with(@target, "#' + footnote_id + '")]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
                if len(link_elements) > 0:
                    link_element = link_elements.pop()
                    link_target = link_element.get('target')
                    link_number = link_element.get('n')

            if footnote_id is None or link_target is None or link_number is None:
                # If the ID cannot be extracted (or the reference to the line element cannot be resolved), simply reference the parent element

                # Attempt to retrieve the parent line
                parent_elements = element.xpath('..', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
                parent_element = parent_elements.pop()

                # Use the parent element's ID as the reference
                parent_number = parent_element.get('n')
                if parent_number is None:
                    parent_id = parent_element.get('{%s}id' % 'http://www.w3.org/XML/1998/namespace')
                    footnote_ref = parent_id
                else:
                    # parent_index = int(parent_number) - 1
                    footnote_ref = int(parent_number)

                # There are probably cases in which <note @type="head"> children also feature footnotes
                # @todo Resolve
                
#                if line_index <= len(self.body.lines):
#                    print 'Adding a footnote for the line ' + str(line_index)
#                    self.body.lines[line_index].footnotes.append(line)

#                    print 'Added the following footnotes:'
#                    self.body.lines[line_index].footnotes

#                    self.footnotes.lines[line_index] = line
#                    print self.footnotes.lines

            else:
                # target_id = link_target.split(' ')[-1]
                # footnote_ref = target_id
                footnote_ref = int(link_number)

                link_index = int(link_number) - 1

                # Retrieve the distance from the parent
                if element.getparent().text is not None:
                    distance_from_parent = len(element.getparent().text)

            line = FootnoteLine(line_value, footnote_index, footnote_ref, distance_from_parent, tokenizer=self.tokenizer, tagger=self.tagger, classes=line_classes, markup=line_markup)

            self.footnotes.lines[footnote_ref] = line

            # Ensure that the footnote element is removed
            element.getparent().remove(element)

    def tokenize(self):

        self.tokenize_titles()
        self.tokenize_headnotes()
        self.tokenize_footnotes()
        self.tokenize_body()

class TextJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Text):
            return {
                'id': obj.id,
                'titles':  map(lambda line: LineJSONEncoder().encode(line), obj.titles.lines) ,
                'title_footnotes':  map(lambda line: LineJSONEncoder().encode(line), obj.title_footnotes.lines) ,
                'headnotes':  map(lambda line: LineJSONEncoder().encode(line), obj.headnotes.lines) ,
                'body':  map(lambda line: LineJSONEncoder().encode(line), obj.body.lines) ,
                'footnotes':  map(lambda line: LineJSONEncoder().encode(line), obj.footnotes.lines)
                }
        return json.JSONEncoder.default(self, obj)
