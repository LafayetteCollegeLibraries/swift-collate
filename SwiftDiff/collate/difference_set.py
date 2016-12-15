
from difference_line import DifferenceLine, DifferenceLineJSONEncoder
from ..text import LineJSONEncoder
import json

class DifferenceSet(object):

    def __init__(self, base_line, variant_lines=[], tokenizer=None, tagger=None):

        self.base_line = base_line
        self.base_line.tokenize()
        self.variant_lines = variant_lines
        self.tokenizer = tokenizer
        self.tagger = tagger

    def add_variant_line(self, line, variant_text_id):

        diff_line = DifferenceLine(self.base_line, line, self.tokenizer, self.tagger)
        # @todo Refactor for the Line constructor
        diff_line.id = variant_text_id
        self.variant_lines.append(diff_line)

    def tokenize(self):
        """Find the differences between each variant line and the base line

        """

        for diff_line in self.variant_lines:

            diff_line.tokenize()

class DifferenceSetJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, DifferenceSet):
            return {
                'base_line': json.loads(LineJSONEncoder().encode(obj.base_line)),
                'variant_lines': map(lambda variant_line: json.loads(DifferenceLineJSONEncoder().encode(variant_line)), obj.variant_lines),
                }
        return json.JSONEncoder.default(self, obj)
