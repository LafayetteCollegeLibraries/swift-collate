import fnmatch
import os
import json

from difference_text import DifferenceText, DifferenceTextJSONEncoder
from difference_line import DifferenceLineJSONEncoder

class CollatedTexts:

    def __init__(self):
        self.lines = {}

    def line(self, line_id):

        if not line_id in self.lines:

            self.lines[line_id] = { 'line': None }

        return self.lines[line_id]

class CollatedLines:

    def __init__(self):

        self.witnesses = []

        # dicts cannot be ordered
        self._witness_index = {}

    def witness_index(self, witness_id):
        """Retrieve the index for any given witness ID

        """

        if not witness_id in self._witness_index:
            index = len(self._witness_index.keys())
            self._witness_index[witness_id] = index

            # Work-around
            self.witnesses.append(None)
        else:
            index = self._witness_index[witness_id]

        return index

    def insert(self, diff_line, witness_id):
        """Insert a DifferenceLine instance to any given witness

        """

        witness_value = self.witness(witness_id)
        print witness_value

        witness_value['line'] = diff_line
        print witness_value

    def witness(self, witness_id):
        """Retrieve the witness structure for any given ID

        """

        # Retrieve the index for the witness id
        witness_index = self.witness_index(witness_id)

        self.witnesses[witness_index] = { 'line': None, 'id': witness_id, 'position': None }

        return self.witnesses[witness_index]

class Collation:

    def transcript_path(self, transcript_id):
        if self.transcript_id is None:

            uri = ''

            for root, dirs, files in os.walk(self.tei_dir_path):
                for d in dirs:
                    if os.path.isfile( os.path.join(root, d, transcript_id + '.tei.xml') ):
                        uri = d + '/' + transcript_id
            return uri

        else:
            return self.transcript_id

    def __init__(self, poem_id, base_text, diffs, tei_dir_path, uri_base=''):
        """Create a Collation for a base text and the associated diffs

        Args:
            poem_id (str): The ID for the poem
            base_text (BaseText): The Document used as a base text
            diffs (Diffs): The diffs used for the other documents
            tei_dir_path (str): The path for the directory containing the encoded TEI Documents
            uri_base (str): The URI segment used in constructing the URI's to the transcripts

        """

        self.transcript_id = None
        self.poem_id = poem_id

        self.base_id = base_text.id

        self.titles = {}
        self.headnotes = {}
        self.body = {}

        self.title_footnotes = []
        self.footnotes = {}
        self.witnesses = []

        # dicts cannot be ordered
        self._title_footnote_index = {}
        self._footnote_index = {}
        self._witness_index = {}

        self.tei_dir_path = tei_dir_path

        # Alignment must take place at this level
#        for diff in diffs:

            # Align the lines within the tokens
#            for line_id, diff_line in diff.body.lines.iteritems():

#                print diff_line.tokens
#                print diff_line.base_line.tokens

        for diff in diffs:

            # Structure the difference set for titles
            for title_line_key, diff_line in diff.titles.lines.iteritems():
                diff_line.uri = uri_base + '/' + diff.other_text.id

                title_line_index = title_line_key

                self.title_line(title_line_index).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(title_line_index)['line'] = diff_line

            # Structure the difference set for title footnotes
            for title_footnote_line_key, diff_line in diff.title_footnotes.lines.iteritems():
                diff_line.uri = uri_base + '/' + diff.other_text.id

                title_footnote_line_index = title_footnote_line_key

                self.title_footnote_line(title_footnote_line_index).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(title_footnote_line_index)['line'] = diff_line

            # Structure the difference set for headnotes
            for headnote_line_index, diff_line in diff.headnotes.lines.iteritems():
                diff_line.uri = uri_base + '/' + diff.other_text.id

                self.headnote_line(headnote_line_index).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(headnote_line_index)['line'] = diff_line

            # Structure the difference set for footnotes
            for line_key, diff_line in diff.footnotes.lines.iteritems():

                diff_line.uri = uri_base + '/' + diff.other_text.id

                # Attempt to provide basic linking for the footnotes
                #
                footnote_line_index = line_key
#                line_values = line_key.split('#')
#                if len(line_values) == 3:

#                    index, target, distance = line_values
#                    target_segments = target.split('-')

#                    if len(target_segments) == 2:

#                        target_index = target_segments[-1]

                        # Retrieve the type of structure
#                        target_structure = target_segments[-2]

#                        diff_line.position = distance + ' characters into ' + target_structure + ' ' + target_index
#                    else:
#                        print 'The target for the footnote link could not be parsed: ' + ', '.join(target_segments)
#                else:
#                    print 'The key for the footnote link could not be parsed: ' + ', '.join(line_values)

                # Collated footnote line tokens
                #
                # CollatedLines
                footnote_lines = self.footnote_line(footnote_line_index)
                footnote_lines.insert(diff_line, diff.other_text.id)
                self.footnotes[footnote_line_index].append( footnote_lines )

            # Structure the difference set for indexed lines
            for line_id, diff_line in diff.body.lines.iteritems():
                diff_line.uri = uri_base + '/' + diff.other_text.id

                print 'ID for the base line: '
                print diff.base_text.id
                print 'ID for the line: '
                print diff.other_text.id

                # print 'Structuring collated lines'
                # print diff_line.base_line.value

                # print diff_line.value

                # self.body_line(line_id).witness(diff.base_text.id)['line'] = diff_line
                base_witness = self.body_line(line_id).witness(diff.base_text.id)
                base_witness['line'] = diff_line
                other_witness = self.body_line(line_id).witness(diff.other_text.id)
                other_witness['line'] = diff_line

                # self.witness(diff.other_text.id).line(line_id)['line'] = diff_line
                other_line = self.witness(diff.other_text.id).line(line_id)
                other_line['line'] = diff_line
                base_line = self.witness(diff.base_text.id).line(line_id)
                base_line['line'] = diff_line

                # collated_lines = self.body_line(line_id)
                # collated_lines.witnesses.append(diff_line)

                # diff_line.uri = uri_base + '/' + diff.base_text.id
                # collated_lines.witnesses.append(diff_line)

                print 'Collated lines for ' + str(line_id)
                print self.body[line_id].witnesses
                for witness in self.body[line_id].witnesses:
                    print witness['line']

    #
    def title_footnote_line(self, line_id):
        """Sets and retrieves the set of collated lines for a footnote in the base text
    
        :param line_id: The key for the footnote
        :type line_id: str.
        :returns:  CollatedLines -- the set of collated lines for the footnotes.

        """

        # Retrieve the index for the footnote id
        index = self.title_footnote_index(line_id)

        if index >= len(self.title_footnotes) - 1:
            self.title_footnotes[index] = CollatedLines()

        return self.title_footnotes[index]

    # Retrieve the index for the title footnotes
    def title_footnote_index(self, footnote_id):
        """Retrieves an index for the ordering of footnotes
    
        :param footnote_id: The key for the footnote
        :type footnote_id: str.
        :returns:  int -- the index for the list of sorted collated footnotes

        """
        if not footnote_id in self._title_footnote_index:
            index = len(self._title_footnote_index.keys())
            self._title_footnote_index[footnote_id] = index

            # Work-around
            self.title_footnotes.append(None)
        else:
            index = self._title_footnote_index[footnote_id]

        return index

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
#        index = self.footnote_index(line_id)

#        if index >= len(self.footnotes) - 1:
#            self.footnotes[index] = CollatedLines()
#        if index >= len(self.footnotes) - 1:
#            self.footnotes[index] = CollatedLines()

#        return self.footnotes[index]

        footnotes_in_line = self.footnote_lines(line_id)
        if len(footnotes_in_line) == 0:
            footnotes_in_line.append(CollatedLines())

        return footnotes_in_line[-1]

    def footnote_lines(self, line_id):
        """

        """

        if not line_id in self.footnotes:
            self.footnotes[line_id] = []
            lines = []
        else:
            lines = self.footnotes[line_id]

        return lines

    def title_line(self, line_id):

        if not line_id in self.titles:

            self.titles[line_id] = CollatedLines()

        return self.titles[line_id]

    def headnote_line(self, line_id):

        if not line_id in self.headnotes:

            self.headnotes[line_id] = CollatedLines()

        return self.headnotes[line_id]

    def body_line(self, line_id):
        """Retrieve the set of collated lines (structured using a CollatedLines Object) at a given line

        """

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
        """Retrieve the set of collated texts (structured using a CollatedTexts Objects) using a witness identifier

        """

        # Retrieve the index for the witness id
        self.witnesses[self.witness_index(witness_id)] = CollatedTexts()

        return self.witnesses[self.witness_index(witness_id)]

class CollatedLinesJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, CollatedLines):
            return {
                'witnesses': map(lambda witness: json.loads(DifferenceLineJSONEncoder().encode(witness)), obj.witnesses)
                }
        return json.JSONEncoder.default(self, obj)

class CollationJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Collation):
            return {
                'titles': map(lambda item: { item[0]: json.loads(CollatedLinesJSONEncoder().encode(item[1])) }, obj.titles.iteritems()),
#                'title_footnotes': obj.title_footnotes,
                'headnotes': map(lambda item: { item[0]: json.loads(CollatedLinesJSONEncoder().encode(item[1])) }, obj.headnotes.iteritems()),
                'body': map(lambda item: { item[0]: json.loads(CollatedLinesJSONEncoder().encode(item[1])) }, obj.body.iteritems()),
                'footnotes': map(lambda element: CollatedLinesJSONEncoder().encode(element), obj.footnotes)
                }
        return json.JSONEncoder.default(self, obj)
