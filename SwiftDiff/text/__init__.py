
import re
from token import Token
from line import Line, FootnoteLine
from lxml import etree

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

    def __init__(self, doc, doc_id, tokenizer):

        self.titles = Titles()
        self.title_footnotes = Footnotes()
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
            
            # element_text = '*' + element_text
            # element_text = '<FOOTNOTE>'
            # element_text = '<' + element_text + '>'
            element_text = ''

            class_ends = self.markup_starts + len(element_text)

            _result_markup['footnote'] = [{
                    
                    'markup' : { 'a': { 'class': 'glyphicon glyphicon-hand-down', 'href': '#footnote-' + element_text } },
                    'range' : { 'start':self.markup_starts, 'end':class_ends }
                    }]

            self.markup_starts = class_ends + 1

        elif element_tag_name == 'lb':
            # Ensures that line breaks are tokenized as blank spaces (" ")
            # Resolves SPP-609
            element_text = ' '
            
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
            line_index = element.get('{%s}id' % 'http://www.w3.org/XML/1998/namespace')

            line = Line(line_value, line_index, tokenizer=self.tokenizer, classes=line_classes, markup=line_markup)

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

            line = Line(line_value, line_index, tokenizer=self.tokenizer, classes=line_classes, markup=line_markup)

            self.headnotes.lines.append( line )

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

                # ref_elements[0].getparent().remove(ref_elements[0])
                # We now preserve the <ref> elements
                # @resolves SPP-597
                #
                pass

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

            if len(link_elements) > 0:
                link_element = link_elements[0]
                link_target = link_element.get('target')
                target_id = link_target.split(' ')[-1]

                # Retrieve the distance from the parent
                if element.getparent().text is None:

                    distance_from_parent = 0
                else:
                
                    distance_from_parent = len(element.getparent().text)

                line = FootnoteLine(line_value, line_index, target_id, distance_from_parent, tokenizer=self.tokenizer, classes=line_classes, markup=line_markup)

                if re.match(r'.+\-title\-', target_id):

                    self.title_footnotes.lines.append( line )
                else:

                    # There are probably cases in which <note @type="head"> children also feature footnotes
                    # @todo Resolve
                    self.footnotes.lines.append( line )

            element.getparent().remove(element)

    def tokenize(self):

        self.tokenize_footnotes()
        self.tokenize_titles()
        self.tokenize_headnotes()
        self.tokenize_body()
