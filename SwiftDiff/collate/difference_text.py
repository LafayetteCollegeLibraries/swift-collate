
from difference_set import DifferenceSet, DifferenceSetJSONEncoder
from difference_line import DifferenceLine
from difference_line import DifferenceLineJSONEncoder
import json
# from collatex import collate_pretokenized_json, Collation, collate, AlignmentTable, Row, Witness, display_alignment_table_as_json

from ..text import Line

class DifferenceText(object):

    def __init__(self, base_text, other_texts=[], tokenizer=None, tagger=None):
        """Create a structure for capturing the differents between the various elements of a Text

        Args:
            base_text (Text): The Document used as a base text
            other_text (Text): The Document used as the variant text
            tokenizer (obj): The tokenizer used in the extraction of features from each line within the texts
            tagger (obj): The part-of-speech tagger used in the analysis of each token

        """

        self.base_text = base_text
        self.other_texts = other_texts
        self.tokenizer = tokenizer
        self.tagger = None

        self.titles = []
        self.headnotes = []
        self.body = []
        self.footnotes = {}

        # Attempt to align the titles
#        if len(base_text.titles.lines) == 0:
#            base_text.titles.lines = map(lambda line: Line('', line.index, tokenizer=line.tokenizer.__class__, tagger=line.tagger), other_text.titles.lines)
#        else:
            # This attempts to align the length of the base text title with that of the variant text
#            base_text.titles.lines = base_text.titles.lines[0:len(other_text.titles.lines)]

        # Iterate through each title
        for title_line_index, title_line in enumerate(base_text.titles.lines):

            title_diffs = DifferenceSet(title_line, [], tokenizer=self.tokenizer, tagger=self.tagger)

            # Iterate through the titles for each variant text
            # Iterate through each text
            for other_text in self.other_texts:

                if len(other_text.titles.lines) - 1 >= title_line_index:

                    variant_title = other_text.titles.lines[title_line_index]
                    title_diffs.add_variant_line(variant_title, other_text.id)

            self.titles.append(title_diffs)
            

        # Only invoke the tokenization for each section of the text after the "map" operation has completed

        # Iterate through each headnote
        for headnote_line_index, headnote_line in enumerate(base_text.headnotes.lines):

            headnote_diffs = DifferenceSet(headnote_line, [], tokenizer=self.tokenizer, tagger=self.tagger)

            # Iterate through the headnotes for each variant text
            # Iterate through each text
            for other_text in self.other_texts:

                if len(other_text.headnotes.lines) - 1 >= headnote_line_index:

                    variant_headnote = other_text.headnotes.lines[headnote_line_index]
                    headnote_diffs.add_variant_line(variant_headnote, other_text.id)

            self.headnotes.append(headnote_diffs)

        # Attempt to align the lines within the body
        # Ensure that the lines are of a matching length
#        if len(base_text.body.lines) == 0:
#            base_text.body.lines = map(lambda line: Line('', line.index, tokenizer=line.tokenizer.__class__, tagger=line.tagger), other_text.body.lines)
#        else:
            # This attempts to align the length of the base text title with that of the variant text
#            base_text.body.lines = base_text.body.lines[0:len(other_text.body.lines)]

        # Iterate through each line in the body
        for line_index, line in enumerate(base_text.body.lines):

            line_diffs = DifferenceSet(line, [], tokenizer=self.tokenizer, tagger=self.tagger)

            # Iterate through the lines for each variant text
            # Iterate through each text
            for other_text in self.other_texts:

                if len(other_text.body.lines) - 1 >= line_index:

                    variant_line = other_text.body.lines[line_index]
                    line_diffs.add_variant_line(variant_line, other_text.id)

            self.body.append(line_diffs)

        # Iterate through each footnote
        for footnote_line_ref, footnote_line in base_text.footnotes.lines.iteritems():

            footnote_diffs = DifferenceSet(footnote_line, [], tokenizer=self.tokenizer, tagger=self.tagger)

            # Iterate through the footnotes for each variant text
            # Iterate through each text
            for other_text in self.other_texts:

                if footnote_line_ref in other_text.footnotes.lines:

                    variant_footnote = other_text.footnotes.lines[footnote_line_ref]
                    footnote_diffs.add_variant_line(variant_footnote, other_text.id)

            # Footnotes are the anomalous case
            self.footnotes[footnote_line_ref] = footnote_diffs

    def collate_lines(self, witnesses):

        normalized_witnesses = []
        tokenized_witnesses = []
        for witness in witnesses:
            normalized_tokens = []
            tokenized_witness = []
            sigil = witness["id"]
            for token in witness["tokens"]:
                tokenized_witness.append(token)
                if "n" in token:
                    normalized_tokens.append(token["n"])
                else:
                    normalized_tokens.append(token["t"])
                pass
            normalized_witnesses.append(Witness(sigil, " ".join(normalized_tokens)))
            tokenized_witnesses.append(tokenized_witness)
        collation = Collation()
        for normalized_witness in normalized_witnesses:
            if normalized_witness.content:
                collation.add_witness(normalized_witness.sigil, normalized_witness.content)

        results = {
            "witnesses": [],
            "table": [[]],
            "status": []
        }
        if len(collation.witnesses) > 0:
            at = collate(collation, output="novisualization", segmentation=False)
            tokenized_at = AlignmentTable(collation)
            for row, tokenized_witness in zip(at.rows, tokenized_witnesses):

                new_row = Row(row.header)
                tokenized_at.rows.append(new_row)
                token_counter = 0

                for cell in row.cells:
                    if cell != "-":
                        if token_counter <= len(tokenized_witness) - 1:
                            new_row.cells.append(tokenized_witness[token_counter])
                            token_counter+=1
                    else:
                        # TODO: should probably be null or None instead, but that would break the rendering at the moment
                        new_row.cells.append({"t":"-"})

            results = display_alignment_table_as_json(tokenized_at)
        return results

    def collate_body(self):

        collated_body = []

        for line_index, line in enumerate(self.base_text.body.lines):
            witnesses = []

            base_tokens = map(lambda token: { 't': token.value }, line.tokens)
            base_witness = { 'id': self.base_text.id, 'tokens': base_tokens }
            witnesses.append(base_witness)

            for other_text in self.other_texts:
                other_tokens = []

                if line_index <= len(other_text.body.lines) - 1:
                    line = other_text.body.lines[line_index]
                    line.tokenize()
                    other_tokens = map(lambda token: { 't': token.value }, line.tokens)
                    other_witness = { 'id': other_text.id, 'tokens': other_tokens }
                    witnesses.append(other_witness)

            collated_body.append(self.collate_lines(witnesses))

        return collated_body

    def collate_headnotes(self):

        collated_headnotes = []

        for line_index, line in enumerate(self.base_text.headnotes.lines):
            witnesses = []

            base_tokens = map(lambda token: { 't': token.value }, line.tokens)
            base_witness = { 'id': self.base_text.id, 'tokens': base_tokens }
            witnesses.append(base_witness)

            for other_text in self.other_texts:
                other_tokens = []

                if line_index <= len(other_text.headnotes.lines) - 1:
                    line = other_text.headnotes.lines[line_index]
                    line.tokenize()
                    other_tokens = map(lambda token: { 't': token.value }, line.tokens)
                    other_witness = { 'id': other_text.id, 'tokens': other_tokens }
                    witnesses.append(other_witness)

            collated_headnotes.append(self.collate_lines(witnesses))

        return collated_headnotes

    def collate_titles(self):

        collated_titles = []

        for line_index, line in enumerate(self.base_text.titles.lines):
            witnesses = []

            base_tokens = map(lambda token: { 't': token.value }, line.tokens)
            base_witness = { 'id': self.base_text.id, 'tokens': base_tokens }
            witnesses.append(base_witness)

            for other_text in self.other_texts:
                other_tokens = []

                if line_index <= len(other_text.titles.lines) - 1:
                    line = other_text.titles.lines[line_index]
                    line.tokenize()
                    other_tokens = map(lambda token: { 't': token.value }, line.tokens)
                    other_witness = { 'id': other_text.id, 'tokens': other_tokens }
                    witnesses.append(other_witness)

            collated_titles.append(self.collate_lines(witnesses))

        return collated_titles

    def collate(self):

#        { "witnesses" :
#              [
#                {
#                    "id" : "A",
#                    "tokens" : [
#                        { "t" : "A", "ref" : 123 },
#                        { "t" : "black" , "adj" : true },
#                        { "t" : "cat", "id" : "xyz" }
#                    ]
#                },
#              ]
#        }

        collation_witnesses = [ self.base_text ].extend(self.other_texts)

        # self.titles = Titles()
        # self.title_footnotes = Footnotes()
        # self.headnotes = Headnotes()
        # self.body = Body()
        # self.footnotes = Footnotes()

        witnesses = []
        collation = Collation()

        self.collate_titles()
#        self.collate_title_footnotes()
        self.collate_headnotes()
        self.collate_body()
#        self.collate_footnotes()

    def merge(self, new_diff_text):

        # Iterate through the titles
        for title_line_index, new_title_diff in enumerate(new_diff_text.titles):

            # Use this DifferenceText as the base
            old_title_diff = self.titles[title_line_index]

            # Add all of the variant lines for the new DifferenceText
#            old_title_diff.variant_lines.extend(new_title_diff.variant_lines)
            for new_variant_title in new_title_diff.variant_lines:
                old_title_diff.variant_lines.append(new_variant_title)

            old_title_diff.align()

        # Iterate through the headnotes
        for headnote_line_index, new_headnote_diff in enumerate(new_diff_text.headnotes):

            # Use this DifferenceText as the base
            old_headnote_diff = self.headnotes[headnote_line_index]

            # Add all of the variant lines for the new DifferenceText
            # old_headnote_diff.variant_lines.extend(new_headnote_diff.variant_lines)
            for new_variant_headnote in new_headnote_diff.variant_lines:
                old_headnote_diff.variant_lines.append(new_variant_headnote)

            old_headnote_diff.align()

        # Iterate through the lines
        for line_index, new_line_diff in enumerate(new_diff_text.body):

            # Use this DifferenceText as the base
            old_line_diff = self.body[line_index]

            # Add all of the variant lines for the new DifferenceText
            # old_line_diff.variant_lines.extend(new_line_diff.variant_lines)
            for new_variant_line in new_line_diff.variant_lines:
                old_line_diff.variant_lines.append(new_variant_line)

            old_line_diff.align()

        # Iterate through the footnotes
        for footnote_line_ref, new_footnote_diff in new_diff_text.footnotes.iteritems():

            # Use this DifferenceText as the base
            old_footnote_diff = self.footnotes[footnote_line_ref]

            # Add all of the variant lines for the new DifferenceText
            # old_footnote_diff.variant_lines.extend(new_footnote_diff.variant_lines)
            for new_variant_footnote in new_footnote_diff.variant_lines:
                old_footnote_diff.variant_lines.append(new_variant_footnote)

            old_footnote_diff.align()

        self.other_texts.extend(new_diff_text.other_texts)

    def tokenize(self):
        """Find each set of differences between the base line and all variants for all titles, headnotes, body lines, and footnotes

        """

        for title_diff in self.titles:
            title_diff.tokenize()
        for headnote_diff in self.headnotes:
            headnote_diff.tokenize()
        for line_diff in self.body:
            line_diff.tokenize()
        for footnote_diff in self.footnotes.itervalues():
            footnote_diff.tokenize()

class DifferenceTextJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, DifferenceText):
            return {
                'titles': map(lambda element: json.loads(DifferenceSetJSONEncoder().encode(element)), obj.titles),
                'headnotes': map(lambda element: json.loads(DifferenceSetJSONEncoder().encode(element)), obj.headnotes),
                'body': map(lambda element: json.loads(DifferenceSetJSONEncoder().encode(element)), obj.body),
                'footnotes': map(lambda item: { item[0]: json.loads(DifferenceSetJSONEncoder().encode(item[1])) }, obj.footnotes.iteritems())
                }
        return json.JSONEncoder.default(self, obj)
