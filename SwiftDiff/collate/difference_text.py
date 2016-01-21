
from difference_set import DifferenceSet
from difference_line import DifferenceLine

class DifferenceText(object):

    def __init__(self, base_text, other_text, tokenizer):

        self.other_text = other_text
        self.tokenizer = tokenizer

        self.titles = DifferenceSet()
        self.title_footnotes = DifferenceSet()
        self.headnotes = DifferenceSet()
        self.body = DifferenceSet()
        self.footnotes = DifferenceSet()

        base_text.titles.lines = base_text.titles.lines[0:len(other_text.titles.lines)]

        # This retrieves the titles from the text
        for title_line_index, title_line in enumerate(base_text.titles.lines):

            # Retrieve the line from the base text
            this_title_line = base_text.titles.lines[title_line_index]

            # Work-arounds for the sorting of lines by index
            other_title_line = other_text.titles.lines[title_line_index]

            try:

                diff_line = DifferenceLine(this_title_line, other_title_line, tokenizer)
            except Exception as ex:
                print 'Failed to structure the titles %s' % ex
                pass

            try:
                diff_line.tokenize()

                # Construct the key from the index of the footnote concatenated to the ID for the line, concatenated to the character distance
                # footnote_key = str(footnote_line_index + 1) + this_footnote_line.target_id + '#' + str(this_footnote_line.distance_from_parent)
                self.titles.lines[title_line_index] = diff_line

            except Exception as ex:
                print 'Failed to tokenize the titles %s' % ex
                pass

        base_text.title_footnotes.lines = base_text.title_footnotes.lines[0:len(other_text.title_footnotes.lines)]

        # This retrieves the footnotes from the text
        for footnote_line_index, footnote_line in enumerate(base_text.title_footnotes.lines):

            # Retrieve the line from the base text
            this_footnote_line = base_text.title_footnotes.lines[footnote_line_index]

            try:

                other_footnote_line = other_text.title_footnotes.lines[footnote_line_index]

                diff_line = DifferenceLine(this_footnote_line, other_footnote_line, tokenizer)
                diff_line.tokenize()

                # Construct the key from the index of the footnote concatenated to the ID for the line, concatenated to the character distance
                footnote_key = str(footnote_line_index + 1) + this_footnote_line.target_id + '#' + str(this_footnote_line.distance_from_parent)

                self.title_footnotes.lines[footnote_key] = diff_line
            except Exception as ex:
                print 'Failed to collate the footnotes within titles %s' % ex
                pass

        base_text.headnotes.lines = base_text.headnotes.lines[0:len(other_text.headnotes.lines)]

        # This retrieves the headnotes from the text
        for headnote_line_index, headnote_line in enumerate(base_text.headnotes.lines):

            base_headnote_line = base_text.headnotes.lines[headnote_line_index]

            # Work-arounds for the sorting of lines by index
            try:
                other_headnote_line = other_text.headnotes.lines[headnote_line_index]
                diff_line = DifferenceLine(base_headnote_line, other_headnote_line, tokenizer)
                diff_line.tokenize()

                # Construct the key from the index of the footnote concatenated to the ID for the line, concatenated to the character distance
                # footnote_key = str(footnote_line_index + 1) + this_footnote_line.target_id + '#' + str(this_footnote_line.distance_from_parent)

                self.headnotes.lines[headnote_line_index] = diff_line
            except Exception as ex:
                print 'Failed to collate the headnotes %s' % ex
                pass

        base_text.footnotes.lines = base_text.footnotes.lines[0:len(other_text.footnotes.lines)]

        # This retrieves the footnotes from the text
        for footnote_line_index, footnote_line in enumerate(base_text.footnotes.lines):

            # Retrieve the line from the base text
            this_footnote_line = base_text.footnotes.lines[footnote_line_index]

            # Work-arounds for the sorting of lines by index
            try:
                other_footnote_line = other_text.footnotes.lines[footnote_line_index]
                # diff_line = DifferenceLine(other_footnote_line, this_footnote_line, tokenizer)
                diff_line = DifferenceLine(this_footnote_line, other_footnote_line, tokenizer)
                diff_line.tokenize()

                # Construct the key from the index of the footnote concatenated to the ID for the line, concatenated to the character distance
                footnote_key = str(footnote_line_index + 1) + this_footnote_line.target_id + '#' + str(this_footnote_line.distance_from_parent)

                self.footnotes.lines[footnote_key] = diff_line
            except Exception as ex:
                print 'Failed to collate the footnotes %s' % ex
                pass

        base_text.body.lines = base_text.body.lines[0:len(other_text.body.lines)]

        # This retrieves the lines from the body
        for line_index, line in enumerate(base_text.body.lines):

            # Retrieve the line from the base text
            base_line = base_text.body.lines[line_index]

            # Work-arounds for the sorting of lines by index
            # if line_index == 0: continue

            try:
                other_line = other_text.body.lines[line_index]
                # diff_line = DifferenceLine(other_line, base_line, tokenizer)
                diff_line = DifferenceLine(base_line, other_line, tokenizer)
                diff_line.tokenize()

                self.body.lines[line_index] = diff_line
            except Exception as ex:
                print 'Failed to collate the body %s' % ex
                pass

    def __unicode__(self):

        pass
