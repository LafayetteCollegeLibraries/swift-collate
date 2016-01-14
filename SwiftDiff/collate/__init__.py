import fnmatch
import os

from difference_text import DifferenceText

class CollatedTexts:

    def __init__(self):

        self.lines = {}
        pass

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
        self.witnesses[self.witness_index(witness_id)] = { 'line': None, 'id': witness_id, 'position': None }

        return self.witnesses[self.witness_index(witness_id)]

class Collation:

    def transcript_path(self, transcript_id):

        uri = ''

        for f in os.listdir(self.tei_dir_path):
            if fnmatch.fnmatch(f, transcript_id + '.tei.xml') and f[0] != '.':

                uri = f
        return uri

    def __init__(self, base_text, diffs, tei_dir_path):

        self.titles = {}
        self.headnotes = {}
        self.body = {}

        self.title_footnotes = []
        self.footnotes = []
        self.witnesses = []

        # dicts cannot be ordered
        self._title_footnote_index = {}
        self._footnote_index = {}
        self._witness_index = {}

        self.tei_dir_path = tei_dir_path

        for diff in diffs:
            
            # Structure the difference set for titles
            for title_line_key, diff_line in diff.titles.lines.iteritems():

                diff_line.uri = '/transcripts/' + self.transcript_path(diff.other_text.id)

                title_line_index = title_line_key

                self.title_line(title_line_index).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(title_line_index)['line'] = diff_line

            # Structure the difference set for title footnotes
            for title_footnote_line_key, diff_line in diff.title_footnotes.lines.iteritems():

                diff_line.uri = '/transcripts/' + self.transcript_path(diff.other_text.id)

                title_footnote_line_index = title_footnote_line_key

                self.title_footnote_line(title_footnote_line_index).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(title_footnote_line_index)['line'] = diff_line

            # Structure the difference set for headnotes
            for headnote_line_index, diff_line in diff.headnotes.lines.iteritems():

                diff_line.uri = '/transcripts/' + self.transcript_path(diff.other_text.id)

                self.headnote_line(headnote_line_index).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(headnote_line_index)['line'] = diff_line

            # Structure the difference set for footnotes
            for line_key, diff_line in diff.footnotes.lines.iteritems():

                diff_line.uri = '/transcripts/' + self.transcript_path(diff.other_text.id)

                index, target, distance = line_key.split('#')
                target_segments = target.split('-')

                target_index = target_segments[-1]

                # Retrieve the type of structure
                target_structure = target_segments[-2]

                # footnote_line_index = index + ' (' + distance + ' characters into ' + target_structure + ' ' + target_index + ')'
                footnote_line_index = line_key

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

                diff_line.uri = '/transcripts/' + self.transcript_path(diff.other_text.id)

                self.body_line(line_id).witness(diff.other_text.id)['line'] = diff_line
                self.witness(diff.other_text.id).line(line_id)['line'] = diff_line

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

    def headnote_line(self, line_id):

        if not line_id in self.headnotes:

            self.headnotes[line_id] = CollatedLines()

        return self.headnotes[line_id]

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
