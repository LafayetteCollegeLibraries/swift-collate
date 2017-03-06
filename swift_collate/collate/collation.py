
from difference_set import DifferenceSet, DifferenceSetJSONEncoder
from difference_line import DifferenceLine
from collated_lines import CollatedLines
from difference_line import DifferenceLineJSONEncoder
import json
from ..text import Line, TextJSONEncoder

class Collation(object):

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

        self.compare(self.other_texts)

    def compare(self, other_texts):

        # Iterate through each title
        for title_line_index, title_line in enumerate(self.base_text['titles']):

            title_line_data = json.loads(title_line)
            collated_titles = CollatedLines(title_line_data, [])

            # Iterate through the titles for each variant text
            # Iterate through each text
            for other_text in other_texts:
                for other_text_title_index, other_text_title_line in enumerate(other_text['titles']):
                    if other_text_title_index == title_line_index:
                        other_title_line_data = json.loads(other_text_title_line)
                        collated_titles.add_variant_line(other_title_line_data)

            self.titles.append(collated_titles.values())

        for headnote_line_index, headnote_line in enumerate(self.base_text['headnotes']):

            headnote_line_data = json.loads(headnote_line)
            collated_headnotes = CollatedLines(headnote_line_data, [])

            # Iterate through the headnotes for each variant text
            # Iterate through each text
            for other_text in other_texts:
                for other_text_headnote_index, other_text_headnote_line in enumerate(other_text['headnotes']):
                    if other_text_headnote_index == headnote_line_index:
                        other_headnote_line_data = json.loads(other_text_headnote_line)
                        collated_headnotes.add_variant_line(other_headnote_line_data)

            self.headnotes.append(collated_headnotes.values())

        # Comparing lines in the body of the text
        for body_line_index, body_line in enumerate(self.base_text['body']):

            body_line_data = json.loads(body_line)
            collated_body_line = CollatedLines(body_line_data, [])

            # Iterate through the body for each variant text
            # Iterate through each text
            for other_text in other_texts:
                for other_text_body_index, other_text_body_line in enumerate(other_text['body']):
                    if other_text_body_index == body_line_index:
                        other_body_line_data = json.loads(other_text_body_line)
                        collated_body_line.add_variant_line(other_body_line_data)

            self.body.append(collated_body_line.values())

        # Comparing footnotes
        for footnote_line_ref, footnote_line in self.base_text['footnotes'].iteritems():

            footnote_line_data = json.loads(footnote_line)
            collated_footnote_line = CollatedLines(footnote_line_data, [])

            # Iterate through the body for each variant text
            # Iterate through each text
            for other_text in other_texts:
                for other_text_footnote_line_ref, other_text_footnote_line in other_text['footnotes'].iteritems():
                    if other_text_footnote_line_ref == footnote_line_ref:
                        other_text_footnote_line_data = json.loads(other_text_footnote_line)
                        collated_footnote_line.add_variant_line(other_text_footnote_line_data)

            self.footnotes[footnote_line_ref] = collated_footnote_line.values()

    def merge(self, new_collation):

        self.compare(new_collation.other_texts)
        self.other_texts.extend(new_collation.other_texts)
